#!/usr/bin/env python3
"""
03 - All MIG RIM IDs found in MVS Script
Extracts all MIG RIM IDs from filtered RIM data and analyzes MVS data.
Shows which MVS Unique IDs are found in RIM set, count of occurrences, and Out of Scope status.
"""

import pandas as pd
import pathlib
import sys
from typing import Set, Dict, List


def extract_rim_ids(rim_file: pathlib.Path) -> Dict[str, int]:
    """Extract all unique RIM IDs from the external_id__c column."""
    print(f"Reading RIM file: {rim_file}")

    df = pd.read_csv(rim_file, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: No 'external_id__c' column found in RIM file")
        sys.exit(1)

    all_ids = {}

    for value in df['external_id__c']:
        if pd.notna(value) and str(value).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(value).split('|') if id_val.strip()]
            for id_val in ids:
                all_ids[id_val] = all_ids.get(id_val, 0) + 1

    print(f"  Extracted {len(all_ids)} unique RIM IDs")
    return all_ids


def load_loader_data(loader_create_file: pathlib.Path, loader_update_file: pathlib.Path) -> tuple[Dict[str, int], Dict[str, int], Dict[str, str], Dict[str, str]]:
    """Load RO Loader data and extract external IDs."""
    print(f"Reading RO Loader Create file: {loader_create_file}")

    # Load RO Loader Create file
    if not loader_create_file.exists():
        print(f"ERROR: RO Loader Create file not found: {loader_create_file}")
        sys.exit(1)

    df_create = pd.read_csv(loader_create_file, encoding='utf-8')

    if 'external_id__v' not in df_create.columns:
        print("ERROR: 'external_id__v' column not found in RO Loader Create file")
        sys.exit(1)

    if 'greenlight_to_implement__c' not in df_create.columns:
        print("ERROR: 'greenlight_to_implement__c' column not found in RO Loader Create file")
        sys.exit(1)

    # Extract Create IDs (handle pipe delimiters) and count occurrences
    create_ids = {}
    create_greenlight = {}

    for _, row in df_create.iterrows():
        external_id = row['external_id__v']
        greenlight_val = row['greenlight_to_implement__c']

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for id_val in ids:
                create_ids[id_val] = create_ids.get(id_val, 0) + 1
                # Store greenlight value for this ID (use first occurrence if multiple)
                if id_val not in create_greenlight:
                    create_greenlight[id_val] = str(greenlight_val).strip() if pd.notna(greenlight_val) else ""

    print(f"  Loaded {len(create_ids)} unique IDs from RO Loader Create")

    # Load RO Loader Update file
    print(f"Reading RO Loader Update file: {loader_update_file}")

    if not loader_update_file.exists():
        print(f"ERROR: RO Loader Update file not found: {loader_update_file}")
        sys.exit(1)

    df_update = pd.read_csv(loader_update_file, encoding='utf-8')

    if 'external_id__c' not in df_update.columns:
        print("ERROR: 'external_id__c' column not found in RO Loader Update file")
        sys.exit(1)

    if 'agi_greenlight_to_implement__c' not in df_update.columns:
        print("ERROR: 'agi_greenlight_to_implement__c' column not found in RO Loader Update file")
        sys.exit(1)

    # Extract Update IDs (handle pipe delimiters) and count occurrences
    update_ids = {}
    update_greenlight = {}

    for _, row in df_update.iterrows():
        external_id = row['external_id__c']
        greenlight_val = row['agi_greenlight_to_implement__c']

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for id_val in ids:
                update_ids[id_val] = update_ids.get(id_val, 0) + 1
                # Store greenlight value for this ID (use first occurrence if multiple)
                if id_val not in update_greenlight:
                    update_greenlight[id_val] = str(greenlight_val).strip() if pd.notna(greenlight_val) else ""

    print(f"  Loaded {len(update_ids)} unique IDs from RO Loader Update")

    return create_ids, update_ids, create_greenlight, update_greenlight


def load_rim_greenlight_data(rim_file: pathlib.Path) -> Dict[str, str]:
    """Load RIM greenlight data for external IDs."""
    print(f"Loading RIM greenlight data from: {rim_file}")

    df = pd.read_csv(rim_file, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in RIM file")
        sys.exit(1)

    if 'greenligh_to_implement__c' not in df.columns:
        print("ERROR: 'greenligh_to_implement__c' column not found in RIM file")
        sys.exit(1)

    rim_greenlight = {}

    for _, row in df.iterrows():
        external_id = row['external_id__c']
        greenlight_val = row['greenligh_to_implement__c']

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for id_val in ids:
                # Store greenlight value for this ID (use first occurrence if multiple)
                if id_val not in rim_greenlight:
                    rim_greenlight[id_val] = str(greenlight_val).strip() if pd.notna(greenlight_val) else ""

    print(f"  Loaded greenlight data for {len(rim_greenlight)} RIM IDs")
    return rim_greenlight


def extract_rim_product_family(rim_file: pathlib.Path) -> Dict[str, str]:
    """Extract product family data from RIM file for external IDs."""
    print(f"Loading RIM product family data from: {rim_file}")

    df = pd.read_csv(rim_file, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in RIM file")
        sys.exit(1)

    if 'product_family__v' not in df.columns:
        print("ERROR: 'product_family__v' column not found in RIM file")
        sys.exit(1)

    rim_product_family = {}

    for _, row in df.iterrows():
        external_id = row['external_id__c']
        product_family_val = row['product_family__v']

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for id_val in ids:
                # Store product family value for this ID (use first occurrence if multiple)
                if id_val not in rim_product_family:
                    rim_product_family[id_val] = str(product_family_val).strip() if pd.notna(product_family_val) else ""

    print(f"  Loaded product family data for {len(rim_product_family)} RIM IDs")
    return rim_product_family


def extract_rim_additional_data(rim_file: pathlib.Path) -> tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Extract additional RIM data: date_of_greenlight__c, additional_implementation_info__c, and id."""
    print(f"Loading additional RIM data from: {rim_file}")

    df = pd.read_csv(rim_file, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in RIM file")
        sys.exit(1)

    rim_greenlight_date = {}
    rim_additional_info = {}
    rim_record_id = {}

    for _, row in df.iterrows():
        external_id = row['external_id__c']
        
        # Get date_of_greenlight__c if exists
        greenlight_date_val = row.get('date_of_greenlight__c', '')
        # Get additional_implementation_info__c if exists
        additional_info_val = row.get('additional_implementation_info__c', '')
        # Get id if exists
        id_val = row.get('id', '')

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for ext_id in ids:
                # Store values for this ID (use first occurrence if multiple)
                if ext_id not in rim_greenlight_date:
                    rim_greenlight_date[ext_id] = str(greenlight_date_val).strip() if pd.notna(greenlight_date_val) else ""
                if ext_id not in rim_additional_info:
                    rim_additional_info[ext_id] = str(additional_info_val).strip() if pd.notna(additional_info_val) else ""
                if ext_id not in rim_record_id:
                    rim_record_id[ext_id] = str(id_val).strip() if pd.notna(id_val) else ""

    print(f"  Loaded additional data for {len(rim_greenlight_date)} RIM IDs")
    return rim_greenlight_date, rim_additional_info, rim_record_id


def is_in_scope_fuzzy(out_of_scope_value: str) -> bool:
    """Check if a value indicates 'In Scope' using fuzzy matching."""
    if pd.isna(out_of_scope_value) or not str(out_of_scope_value).strip():
        return False

    value = str(out_of_scope_value).strip().lower()

    # Fuzzy match for "in scope" variations
    in_scope_patterns = [
        "in scope",
        "inscope",
        "in-scope",
        "scope in",
        "scopein"
    ]

    # Check if any in-scope pattern is found
    for pattern in in_scope_patterns:
        if pattern in value:
            return True

    # Additional check for variations like "scope: in" or "in: scope"
    if "scope" in value and "in" in value:
        # Make sure it's not "out of scope" or similar
        if "out" not in value and "not" not in value:
            return True

    return False





def find_drug_products_in_loader_create_optimized(unique_id: str, df_create: pd.DataFrame, df_drug: pd.DataFrame) -> str:
    """Find drug products for a unique ID through loader create chain using pre-loaded data."""
    if 'external_id__v' not in df_create.columns:
        return ""

    # Find rows where external_id__v contains the unique_id (in pipe-delimited sets)
    matching_external_ids = set()
    for value in df_create['external_id__v']:
        if pd.notna(value) and str(value).strip():
            ids = [id_val.strip() for id_val in str(value).split('|') if id_val.strip()]
            if unique_id in ids:
                matching_external_ids.add(str(value).strip())

    if not matching_external_ids:
        return ""

    if 'regulatory_objective__v' not in df_drug.columns or 'drug_product__v' not in df_drug.columns:
        return ""

    # Find drug products for matching external IDs
    drug_products = set()
    for ext_id in matching_external_ids:
        for _, row in df_drug.iterrows():
            if pd.notna(row['regulatory_objective__v']) and str(row['regulatory_objective__v']).strip() == ext_id:
                if pd.notna(row['drug_product__v']):
                    drug_products.add(str(row['drug_product__v']).strip())

    return " | ".join(sorted(drug_products)) if drug_products else ""


def find_drug_products_in_loader_update_optimized(unique_id: str, df_update: pd.DataFrame, df_drug: pd.DataFrame) -> str:
    """Find drug products for a unique ID through loader update chain using pre-loaded data."""
    if 'external_id__c' not in df_update.columns:
        return ""

    # Find rows where external_id__c contains the unique_id (in pipe-delimited sets)
    matching_external_ids = set()
    for value in df_update['external_id__c']:
        if pd.notna(value) and str(value).strip():
            ids = [id_val.strip() for id_val in str(value).split('|') if id_val.strip()]
            if unique_id in ids:
                matching_external_ids.add(str(value).strip())

    if not matching_external_ids:
        return ""

    if 'regulatory_objective__v' not in df_drug.columns or 'drug_product__v' not in df_drug.columns:
        return ""

    # Find drug products for matching external IDs
    drug_products = set()
    for ext_id in matching_external_ids:
        for _, row in df_drug.iterrows():
            if pd.notna(row['regulatory_objective__v']) and str(row['regulatory_objective__v']).strip() == ext_id:
                if pd.notna(row['drug_product__v']):
                    drug_products.add(str(row['drug_product__v']).strip())

    return " | ".join(sorted(drug_products)) if drug_products else ""








def find_drug_products_in_rim_optimized(unique_id: str, df_rim_ro_filtered: pd.DataFrame, df_drug_join: pd.DataFrame, df_drug_data: pd.DataFrame) -> str:
    """Find drug product names for a unique ID through RIM chain using pre-loaded and pre-filtered data."""
    if 'id' not in df_rim_ro_filtered.columns or 'external_id__c' not in df_rim_ro_filtered.columns:
        return ""

    # Find RIM IDs where external_id__c contains the unique_id (in pipe-delimited sets)
    # Data is already filtered by migration date
    matching_rim_ids = set()
    for _, row in df_rim_ro_filtered.iterrows():
        if pd.notna(row['external_id__c']) and str(row['external_id__c']).strip():
            ids = [id_val.strip() for id_val in str(row['external_id__c']).split('|') if id_val.strip()]
            if unique_id in ids:
                if pd.notna(row['id']):
                    matching_rim_ids.add(str(row['id']).strip())

    if not matching_rim_ids:
        return ""

    if 'regulatory_objective__v' not in df_drug_join.columns or 'drug_product__v' not in df_drug_join.columns:
        return ""

    # Find drug product IDs for matching RIM IDs
    drug_product_ids = set()
    for rim_id in matching_rim_ids:
        for _, row in df_drug_join.iterrows():
            if pd.notna(row['regulatory_objective__v']) and str(row['regulatory_objective__v']).strip() == rim_id:
                if pd.notna(row['drug_product__v']):
                    drug_product_ids.add(str(row['drug_product__v']).strip())

    if not drug_product_ids:
        return ""

    if 'id' not in df_drug_data.columns or 'name__v' not in df_drug_data.columns:
        return ""

    # Find drug product names for matching drug product IDs
    drug_product_names = set()
    for drug_id in drug_product_ids:
        for _, row in df_drug_data.iterrows():
            if pd.notna(row['id']) and str(row['id']).strip() == drug_id:
                if pd.notna(row['name__v']):
                    drug_product_names.add(str(row['name__v']).strip())

    return " | ".join(sorted(drug_product_names)) if drug_product_names else ""








def extract_rim_product_family(rim_file: pathlib.Path) -> Dict[str, str]:
    """Extract product family data from RIM file for external IDs."""
    print(f"Loading RIM product family data from: {rim_file}")

    df = pd.read_csv(rim_file, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in RIM file")
        sys.exit(1)

    if 'product_family__v' not in df.columns:
        print("ERROR: 'product_family__v' column not found in RIM file")
        sys.exit(1)

    rim_product_family = {}

    for _, row in df.iterrows():
        external_id = row['external_id__c']
        product_family_val = row['product_family__v']

        if pd.notna(external_id) and str(external_id).strip():
            # Split by pipe delimiter and clean each ID
            ids = [id_val.strip() for id_val in str(external_id).split('|') if id_val.strip()]
            for id_val in ids:
                # Store product family value for this ID (use first occurrence if multiple)
                if id_val not in rim_product_family:
                    rim_product_family[id_val] = str(product_family_val).strip() if pd.notna(product_family_val) else ""

    print(f"  Loaded product family data for {len(rim_product_family)} RIM IDs")
    return rim_product_family


def load_product_data(product_file: pathlib.Path) -> pd.DataFrame:
    """Load the product data for merging."""
    print(f"Reading product data: {product_file}")

    if not product_file.exists():
        print(f"ERROR: Product file not found: {product_file}")
        sys.exit(1)

    df = pd.read_csv(product_file, encoding='utf-8')

    if 'id' not in df.columns or 'name__v' not in df.columns:
        print("ERROR: Required columns 'id' and 'name__v' not found in product file")
        sys.exit(1)

    print(f"  Loaded {len(df)} product records")
    return df[['id', 'name__v']]


def analyze_mvs_data(mvs_file: pathlib.Path, rim_ids: Dict[str, int], create_ids: Dict[str, int], update_ids: Dict[str, int],
                    create_greenlight: Dict[str, str], update_greenlight: Dict[str, str], rim_greenlight: Dict[str, str],
                    rim_product_family: Dict[str, str], rim_greenlight_date: Dict[str, str], 
                    rim_additional_info: Dict[str, str], rim_record_id: Dict[str, str]) -> List[Dict]:
    """Analyze MVS data to show which MVS IDs are found in RIM set."""
    print(f"Reading MVS file: {mvs_file}")

    df = pd.read_csv(mvs_file, encoding='utf-8')

    # Column names
    unique_id_col = 'Unique ID'
    out_of_scope_col = 'Is the line Out Of Scope of the migration? = no active license or not owned by AGI anymore (divested)'
    green_light_col = 'Green light for change to be implemented at site- by REG\nYES/NO'
    molecule_col = 'Molecule'
    implementation_rules_col = 'Implementation Rules'
    validation_date_col = 'Validation date for Green light for change to be implemented at site- by REG'

    if unique_id_col not in df.columns:
        print("ERROR: 'Unique ID' column not found in MVS file")
        sys.exit(1)

    if out_of_scope_col not in df.columns:
        print("ERROR: Out of Scope column not found in MVS file")
        sys.exit(1)

    if green_light_col not in df.columns:
        print("ERROR: Green light column not found in MVS file")
        sys.exit(1)

    if molecule_col not in df.columns:
        print("ERROR: 'Molecule' column not found in MVS file")
        sys.exit(1)

    print(f"  Analyzing {len(df)} MVS rows against {len(rim_ids)} RIM IDs")



    results = []

    # Group by Unique ID to count occurrences and capture additional columns
    agg_dict = {
        out_of_scope_col: 'first',  # Take first occurrence of Out of Scope value
        green_light_col: 'first',   # Take first occurrence of Green light value
        molecule_col: 'first',      # Take first occurrence of Molecule value
        unique_id_col: 'count'      # Count occurrences
    }
    
    # Add new columns if they exist
    if implementation_rules_col in df.columns:
        agg_dict[implementation_rules_col] = 'first'
    if validation_date_col in df.columns:
        agg_dict[validation_date_col] = 'first'
    
    mvs_grouped = df.groupby(unique_id_col).agg(agg_dict).rename(columns={unique_id_col: 'count'})

    for mvs_id, row in mvs_grouped.iterrows():
        if pd.notna(mvs_id) and str(mvs_id).strip():
            mvs_id_str = str(mvs_id).strip()

            # Get Out of Scope value first to filter
            out_of_scope_value = row[out_of_scope_col]
            if pd.isna(out_of_scope_value):
                out_of_scope_value = ""

            out_of_scope_str = str(out_of_scope_value).strip()



            # Get count of this MVS ID in RIM set
            count_in_rim = rim_ids.get(mvs_id_str, 0)

            # Get count of this MVS ID in RO Loader files
            count_in_create = create_ids.get(mvs_id_str, 0)
            count_in_update = update_ids.get(mvs_id_str, 0)

            # Get greenlight values for this MVS ID
            greenlight_create = create_greenlight.get(mvs_id_str, "")
            greenlight_update = update_greenlight.get(mvs_id_str, "")
            greenlight_rim = rim_greenlight.get(mvs_id_str, "")

            # Get RIM product family for this MVS ID
            rim_product_family_value = rim_product_family.get(mvs_id_str, "")
            
            # Get new RIM fields for this MVS ID
            rim_greenlight_date_value = rim_greenlight_date.get(mvs_id_str, "")
            rim_additional_info_value = rim_additional_info.get(mvs_id_str, "")
            rim_record_id_value = rim_record_id.get(mvs_id_str, "")



            # Get Green light value
            green_light_value = row[green_light_col]
            if pd.isna(green_light_value):
                green_light_value = ""

            # Get Molecule value
            molecule_value = row[molecule_col]
            if pd.isna(molecule_value):
                molecule_value = ""
            
            # Get new MVS columns if they exist
            implementation_rules_value = ""
            if implementation_rules_col in row.index:
                implementation_rules_value = row[implementation_rules_col]
                if pd.isna(implementation_rules_value):
                    implementation_rules_value = ""
            
            validation_date_value = ""
            if validation_date_col in row.index:
                validation_date_value = row[validation_date_col]
                if pd.isna(validation_date_value):
                    validation_date_value = ""

            results.append({
                'MVS_Unique_ID': mvs_id_str,
                'Out_of_Scope': out_of_scope_str,
                'Count_in_MVS': int(row['count']),
                'Count_in_RO_Loader_Create': count_in_create,
                'Count_in_RO_Loader_Update': count_in_update,
                'Count_in_RIM': count_in_rim,
                'Found_in_RIM': 'Yes' if count_in_rim > 0 else 'No',
                'Green_Light_MVS': str(green_light_value).strip(),
                'MVS_Implementation_Rules': str(implementation_rules_value).strip(),
                'MVS_Validation_Date': str(validation_date_value).strip(),
                'Greenlight_RO_Loader_Create': greenlight_create,
                'Greenlight_RO_Loader_Update': greenlight_update,
                'Greenlight_RIM': greenlight_rim,
                'RIM_Date_of_Greenlight': str(rim_greenlight_date_value).strip(),
                'RIM_Additional_Implementation_Info': str(rim_additional_info_value).strip(),
                'RIM_Record_ID': str(rim_record_id_value).strip(),
                'MVS_Molecule': str(molecule_value).strip(),
                'RIM_Product_Family': str(rim_product_family_value).strip(),
                'RIM_Product_Name': ""  # Will be populated by merge_product_family_data
            })

    return sorted(results, key=lambda x: x['MVS_Unique_ID'])

def merge_product_family_data(results: List[Dict], product_df: pd.DataFrame) -> List[Dict]:
    """Merge product family data with the results."""
    print("Merging product family data...")

    # Create a lookup dictionary for product names
    product_lookup = {}
    for _, row in product_df.iterrows():
        if pd.notna(row['id']) and pd.notna(row['name__v']):
            product_lookup[str(row['id']).strip()] = str(row['name__v']).strip()

    # Update results with product names and remove the ID column
    for result in results:
        rim_product_family_id = result.pop('RIM_Product_Family', "")  # Remove the ID column
        if rim_product_family_id:
            product_name = product_lookup.get(rim_product_family_id, "")
            result['RIM_Product_Name'] = product_name
        else:
            result['RIM_Product_Name'] = ""

    print(f"  Merged product family data for {len(results)} records")
    return results





def export_results(results: List[Dict], output_file: pathlib.Path):
    """Export results to CSV file with file lock handling."""
    print(f"Exporting results to: {output_file}")

    results_df = pd.DataFrame(results)

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
        except Exception:
            print(f"ERROR: Could not write file: {output_file}")
            sys.exit(1)

    # Summary statistics
    found_count = len([r for r in results if r['Found_in_RIM'] == 'Yes'])
    not_found_count = len([r for r in results if r['Found_in_RIM'] == 'No'])
    total_mvs_entries = sum(r['Count_in_MVS'] for r in results)

    print(f"  SUCCESS: Exported {len(results)} MVS Unique IDs")
    print(f"  Found in RIM: {found_count}")
    print(f"  Not found in RIM: {not_found_count}")
    print(f"  Total MVS entries: {total_mvs_entries}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("MIG RIM IDs FOUND IN MVS ANALYSIS")
    print("=" * 70)

    # Define file paths
    rim_file = pathlib.Path("03 Target RIM/regulatory_objective__rim.csv")
    mvs_file = pathlib.Path("01 - Append MVS.csv")
    loader_create_file = pathlib.Path("02 Loader sheets/regulatory_objective__rim.csv")
    loader_update_file = pathlib.Path("02 Loader sheets/regulatory_objective_rim_update.csv")
    product_file = pathlib.Path("03 Target RIM/product__v.csv")
    output_file = pathlib.Path("03 - Compare Unique IDs and Green Light.csv")

    # Validate input files
    if not rim_file.exists():
        print(f"ERROR: RIM file not found: {rim_file}")
        sys.exit(1)

    if not mvs_file.exists():
        print(f"ERROR: MVS file not found: {mvs_file}")
        sys.exit(1)

    # Extract RIM IDs
    rim_ids = extract_rim_ids(rim_file)

    if not rim_ids:
        print("ERROR: No RIM IDs found")
        sys.exit(1)

    # Load RO Loader data
    create_ids, update_ids, create_greenlight, update_greenlight = load_loader_data(loader_create_file, loader_update_file)

    # Load RIM greenlight data
    rim_greenlight = load_rim_greenlight_data(rim_file)

    # Load RIM product family data
    rim_product_family = extract_rim_product_family(rim_file)
    
    # Load additional RIM data (date_of_greenlight__c, additional_implementation_info__c, id)
    rim_greenlight_date, rim_additional_info, rim_record_id = extract_rim_additional_data(rim_file)

    # Load product data for merging
    product_df = load_product_data(product_file)

    # Analyze MVS data
    results = analyze_mvs_data(mvs_file, rim_ids, create_ids, update_ids, create_greenlight, update_greenlight, 
                               rim_greenlight, rim_product_family, rim_greenlight_date, rim_additional_info, rim_record_id)

    # Merge product family data
    results = merge_product_family_data(results, product_df)

    # Export results
    export_results(results, output_file)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print(f"Output file: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
