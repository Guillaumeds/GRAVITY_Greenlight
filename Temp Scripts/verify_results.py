#!/usr/bin/env python3
"""
Verify the results of the Drug Product Analysis
"""

import pandas as pd

def verify_results():
    try:
        # Load the results
        df = pd.read_csv("04 - Drug Product Analysis.csv")
        print(f"Total rows: {len(df)}")
        
        # Check for matches
        matches = df[df['Veeva_Value_Label'] != '']
        print(f"Matches found: {len(matches)}")
        
        # Check for product matches
        product_matches = df[df['Product_Match'] == True]
        print(f"Product matches: {len(product_matches)}")
        
        # Show sample matches
        print("\nSample matches:")
        for i, (idx, row) in enumerate(matches.head(5).iterrows()):
            print(f"  {i+1}. MVS_Molecule: {row['MVS_Molecule']}")
            print(f"     RIM_Product: {row['Veeva_Value_Label']}")
            print(f"     Product_Match: {row['Product_Match']}")
            print()
        
        # Check columns
        print("Columns in output:")
        for col in df.columns:
            print(f"  - {col}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_results()
