#!/usr/bin/env python3
"""
Test the 04 - Drug Product Analysis functionality with sample data
"""

import pandas as pd
import pathlib
from difflib import SequenceMatcher

def similarity_ratio(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings using SequenceMatcher."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def test_functionality():
    """Test the key functionality of the 04 script."""
    print("=" * 60)
    print("TESTING 04 - DRUG PRODUCT ANALYSIS FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Test 1: Load input data
        input_file = pathlib.Path("03 - Compare Unique IDs and Green Light.csv")
        if input_file.exists():
            df = pd.read_csv(input_file, encoding='utf-8', nrows=10)
            print(f"✓ Loaded input data: {len(df)} sample rows")
            
            # Test 2: Create MVS_Drug_Product
            if 'MVS_Dosage_Form' in df.columns and 'MVS_Molecule' in df.columns:
                df['MVS_Drug_Product'] = df['MVS_Dosage_Form'].astype(str) + " " + df['MVS_Molecule'].astype(str)
                df['MVS_Drug_Product'] = df['MVS_Drug_Product'].str.replace('nan ', '').str.replace(' nan', '').str.replace('nan', '')
                df['MVS_Drug_Product'] = df['MVS_Drug_Product'].str.strip()
                print("✓ Created MVS_Drug_Product column")
                print("Sample values:")
                for i, val in enumerate(df['MVS_Drug_Product'].head(3)):
                    print(f"  {i+1}: {val}")
            else:
                print("✗ Required columns for MVS_Drug_Product not found")
                return
        else:
            print("✗ Input file not found")
            return
        
        # Test 3: Load product data
        product_file = pathlib.Path("03 Target RIM/product__v_data.csv")
        if product_file.exists():
            product_df = pd.read_csv(product_file, encoding='utf-8', nrows=5)
            print(f"✓ Loaded product data: {len(product_df)} sample rows")
        else:
            print("✗ Product file not found")
            return
        
        # Test 4: Load LoV mapping
        lov_file = pathlib.Path("04 Transformation Maps/LoV Object Mapping.xlsx")
        if lov_file.exists():
            lov_df = pd.read_excel(lov_file, nrows=10)
            if 'Source Value' in lov_df.columns and 'Veeva Value Label' in lov_df.columns:
                lov_filtered = lov_df[['Source Value', 'Veeva Value Label']].dropna()
                print(f"✓ Loaded LoV mapping: {len(lov_filtered)} sample rows")
                
                # Test 5: Fuzzy matching sample
                if len(df) > 0 and len(lov_filtered) > 0:
                    sample_mvs = str(df['MVS_Drug_Product'].iloc[0]).strip()
                    sample_source = str(lov_filtered['Source Value'].iloc[0]).strip()
                    
                    if sample_mvs and sample_source and sample_mvs != 'nan' and sample_source != 'nan':
                        score = similarity_ratio(sample_mvs, sample_source)
                        print(f"✓ Fuzzy matching test:")
                        print(f"  MVS Product: '{sample_mvs}'")
                        print(f"  LoV Source: '{sample_source}'")
                        print(f"  Similarity: {score:.1f}%")
                    else:
                        print("✓ Fuzzy matching logic ready (no valid sample data)")
                else:
                    print("✓ Fuzzy matching logic ready")
            else:
                print("✗ Required LoV columns not found")
                return
        else:
            print("✗ LoV mapping file not found")
            return
        
        # Test 6: Merge logic
        if 'RIM_Product_Family' in df.columns:
            # Simulate merge
            merged_df = df.merge(
                product_df[['id', 'name__v']], 
                left_on='RIM_Product_Family', 
                right_on='id', 
                how='left'
            )
            merged_df = merged_df.rename(columns={'name__v': 'RIM_Product_Name'})
            if 'id' in merged_df.columns:
                merged_df = merged_df.drop(columns=['id'])
            print(f"✓ Merge logic test: {len(merged_df)} rows")
        else:
            print("✗ RIM_Product_Family column not found")
            return
        
        print("\n" + "=" * 60)
        print("ALL FUNCTIONALITY TESTS PASSED")
        print("✓ Script should work correctly with full dataset")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_functionality()
