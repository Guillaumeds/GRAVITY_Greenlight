#!/usr/bin/env python3
"""
04 - Product Data comparison.py

Purpose: Compare MVS molecules with RIM product names to determine matching
Process: Load data from 03 CSV, parse RIM product names, check if all molecules found in MVS data
Success Criteria: Generate CSV with product match TRUE/FALSE/empty based on molecule matching
Logic: Case-insensitive matching, all RIM molecules must be found in MVS for TRUE result
"""

import pandas as pd
import pathlib
import sys
import re
from typing import List, Set


def parse_rim_product_molecules(rim_product_name: str) -> List[str]:
    """
    Parse RIM product name to extract individual molecule names.
    Handles comma-separated molecules and parenthetical content.
    """
    if pd.isna(rim_product_name) or not str(rim_product_name).strip():
        return []
    
    product_name = str(rim_product_name).strip().lower()
    
    # Split by comma to get individual molecules
    molecules = []
    parts = product_name.split(',')
    
    for part in parts:
        part = part.strip()
        
        # Remove parenthetical content (like "(decanoate, isocaproate, phenylpropionate, propionate)")
        # but keep the molecules inside parentheses as separate molecules
        if '(' in part and ')' in part:
            # Extract content inside parentheses
            paren_content = re.findall(r'\((.*?)\)', part)
            if paren_content:
                # Add molecules from inside parentheses
                paren_molecules = paren_content[0].split(',')
                for paren_mol in paren_molecules:
                    paren_mol = paren_mol.strip()
                    if paren_mol:
                        molecules.append(paren_mol)
            
            # Remove parentheses and add the main molecule
            main_part = re.sub(r'\s*\([^)]*\)', '', part).strip()
            if main_part:
                molecules.append(main_part)
        else:
            if part:
                molecules.append(part)
    
    # Clean up molecules - remove extra whitespace and normalize
    cleaned_molecules = []
    for mol in molecules:
        mol = mol.strip()
        if mol:
            # Normalize the molecule name
            normalized = normalize_molecule_name(mol)
            cleaned_molecules.append(normalized)

    return cleaned_molecules


def normalize_molecule_name(molecule: str) -> str:
    """
    Normalize molecule name for better matching.
    Handles common spelling variations and standardizations.
    """
    if not molecule:
        return ""

    molecule = molecule.lower().strip()

    # Handle common spelling variations
    spelling_variations = {
        'indometacin': 'indomethacin',
        'tioguanine': 'thioguanine',
        'sulfamethoxazole': 'sulphamethoxazole',
    }

    for variant, standard in spelling_variations.items():
        if molecule == variant:
            molecule = standard
        elif molecule == standard:
            # Also check reverse mapping
            pass

    return molecule


def extract_mvs_molecules(mvs_molecule: str) -> Set[str]:
    """
    Extract and normalize molecules from MVS molecule string.
    Returns a set of lowercase molecule names for matching.
    """
    if pd.isna(mvs_molecule) or not str(mvs_molecule).strip():
        return set()

    molecule_str = str(mvs_molecule).strip().lower()

    # Split by common separators and extract individual molecules
    molecules = set()

    # Handle various separators
    separators = ['+', '/', ',', ' and ', ' & ']
    parts = [molecule_str]

    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts

    for part in parts:
        part = part.strip()

        # Remove common suffixes/prefixes
        part = re.sub(r'\s+(hydrochloride|hcl|sodium|acetate|phosphate|base|hydrobromide|calcium|decanoate)$', '', part)
        part = part.strip()

        if part:
            # Normalize the molecule name
            normalized = normalize_molecule_name(part)
            molecules.add(normalized)

    return molecules


def check_product_match(mvs_molecule: str, rim_product_name: str) -> str:
    """
    Check if RIM product molecules can be found in MVS molecule data.
    Returns 'TRUE' if all RIM molecules found, 'FALSE' if not, empty if RIM is empty.
    """
    # If RIM product name is empty, return empty
    if pd.isna(rim_product_name) or not str(rim_product_name).strip():
        return ""
    
    # If MVS molecule is empty, return FALSE
    if pd.isna(mvs_molecule) or not str(mvs_molecule).strip():
        return "FALSE"
    
    # Parse RIM product molecules
    rim_molecules = parse_rim_product_molecules(rim_product_name)
    if not rim_molecules:
        return ""
    
    # Extract MVS molecules
    mvs_molecules = extract_mvs_molecules(mvs_molecule)
    if not mvs_molecules:
        return "FALSE"
    
    # Special handling for testosterone case
    # If RIM has testosterone + specific forms, but MVS only has testosterone, that should match
    rim_product_lower = str(rim_product_name).lower()
    if 'testosterone' in rim_product_lower and '(' in rim_product_lower:
        # Check if MVS has testosterone
        for mvs_mol in mvs_molecules:
            if 'testosterone' in mvs_mol:
                return "TRUE"

    # Check if all RIM molecules can be found in MVS molecules
    for rim_mol in rim_molecules:
        rim_mol = rim_mol.strip().lower()
        if not rim_mol:
            continue

        # Skip specific testosterone forms if base testosterone is present
        if rim_mol in ['decanoate', 'isocaproate', 'phenylpropionate', 'propionate']:
            # Check if MVS has testosterone (base molecule)
            has_testosterone = any('testosterone' in mvs_mol for mvs_mol in mvs_molecules)
            if has_testosterone:
                continue  # Skip checking specific forms if base is present

        # Check if this RIM molecule is found in any MVS molecule
        found = False
        for mvs_mol in mvs_molecules:
            if rim_mol in mvs_mol or mvs_mol in rim_mol:
                found = True
                break

        if not found:
            return "FALSE"

    return "TRUE"


def process_product_comparison(input_file: pathlib.Path, output_file: pathlib.Path):
    """Process the product comparison analysis."""
    print("======================================================================")
    print("PRODUCT DATA COMPARISON ANALYSIS")
    print("======================================================================")
    
    # Load input data
    print(f"Reading input file: {input_file}")
    
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    df = pd.read_csv(input_file, encoding='utf-8')
    
    # Validate required columns
    required_columns = ['MVS_Molecule', 'RIM_Product_Name']
    for col in required_columns:
        if col not in df.columns:
            print(f"ERROR: Required column '{col}' not found in input file")
            sys.exit(1)
    
    print(f"  Loaded {len(df)} records")
    
    # Process product matching
    print("Processing product matching...")
    
    results = []
    for idx, row in df.iterrows():
        mvs_molecule = row['MVS_Molecule']
        rim_product_name = row['RIM_Product_Name']
        
        # Perform product matching
        product_match = check_product_match(mvs_molecule, rim_product_name)
        
        # Create result record with all original columns plus new match column
        result = row.to_dict()
        result['Product_Match'] = product_match
        results.append(result)
        
        # Progress indicator
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1:,} records...")
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Export results
    print(f"Exporting results to: {output_file}")
    
    # Handle file lock with retry mechanism
    while True:
        try:
            results_df.to_csv(output_file, index=False, encoding='utf-8')
            break
        except PermissionError:
            print(f"ERROR: File is locked: {output_file}")
            print("Please close the file in Excel and press Enter to retry...")
            input("Press Enter when ready: ")
            continue
        except Exception as e:
            print(f"ERROR: Could not write file: {output_file}")
            print(f"Error details: {e}")
            sys.exit(1)
    
    # Summary statistics
    total_records = len(results_df)
    true_matches = len(results_df[results_df['Product_Match'] == 'TRUE'])
    false_matches = len(results_df[results_df['Product_Match'] == 'FALSE'])
    empty_matches = len(results_df[results_df['Product_Match'] == ''])
    
    print(f"  SUCCESS: Exported {total_records:,} records")
    print(f"  Product matches (TRUE): {true_matches:,}")
    print(f"  Product non-matches (FALSE): {false_matches:,}")
    print(f"  Empty RIM data: {empty_matches:,}")
    
    print("\n======================================================================")
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print(f"Output file: {output_file}")
    print("======================================================================")


def main():
    """Main function to run the product comparison analysis."""
    # Define file paths
    input_file = pathlib.Path("03 - Compare Unique IDs and Green Light.csv")
    output_file = pathlib.Path("04 - Product Data comparison.csv")
    
    # Validate input file
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        print("Please run script 03 first to generate the required input data.")
        sys.exit(1)
    
    # Process the comparison
    process_product_comparison(input_file, output_file)


if __name__ == "__main__":
    main()
