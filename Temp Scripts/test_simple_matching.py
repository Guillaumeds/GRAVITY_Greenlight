#!/usr/bin/env python3
"""
Simple test of the matching logic without multiprocessing
"""

import pandas as pd
from rapidfuzz import fuzz, process

def test_simple_matching():
    print("=" * 50)
    print("TESTING SIMPLE MATCHING")
    print("=" * 50)
    
    try:
        # Load input data
        print("Loading input data...")
        df = pd.read_csv("03 - Compare Unique IDs and Green Light.csv")
        print(f"  Loaded {len(df)} rows")
        
        # Load product data
        print("Loading product data...")
        product_df = pd.read_csv("03 Target RIM/product__v_data.csv")
        print(f"  Loaded {len(product_df)} product records")
        
        # Merge product family data
        print("Merging product family data...")
        df = df.merge(product_df[['id', 'name__v']], 
                     left_on='RIM_Product_Family', 
                     right_on='id', 
                     how='left')
        df.rename(columns={'name__v': 'RIM_Product_Name'}, inplace=True)
        print(f"  Merged data: {len(df)} rows")
        
        # Filter to in-scope only
        in_scope_mask = df['Out_of_Scope'] != 'OOS'
        in_scope_df = df[in_scope_mask].copy()
        print(f"  In-scope records: {len(in_scope_df)}")
        
        # Get unique RIM products for matching
        rim_products = df['RIM_Product_Name'].dropna()
        rim_products = rim_products[rim_products.astype(str).str.strip() != '']
        rim_choices = rim_products.astype(str).str.strip().unique().tolist()
        print(f"  RIM product choices: {len(rim_choices)}")
        
        # Test matching on first 10 records
        print("\nTesting matching on first 10 in-scope records:")
        test_records = in_scope_df.head(10)
        
        matches_found = 0
        for idx, row in test_records.iterrows():
            mvs_molecule = str(row['MVS_Molecule']).strip()
            
            if not mvs_molecule or mvs_molecule == 'nan':
                print(f"  {idx}: No molecule to match")
                continue
                
            print(f"  {idx}: MVS_Molecule = '{mvs_molecule}'")
            
            # Find best match
            best_match = process.extractOne(
                mvs_molecule, 
                rim_choices, 
                scorer=fuzz.ratio, 
                score_cutoff=75
            )
            
            if best_match:
                matched_product, score = best_match[0], best_match[1]
                print(f"       -> Matched: '{matched_product}' (Score: {score:.1f}%)")
                matches_found += 1
            else:
                print(f"       -> No match found above 75%")
        
        print(f"\nFound {matches_found} matches out of 10 test records")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_matching()
