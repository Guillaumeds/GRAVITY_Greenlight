#!/usr/bin/env python3
"""
Verification script for 04 - Drug Product Analysis results
"""

import pandas as pd

def main():
    df = pd.read_csv('04 - Drug Product Analysis.csv')

    print("=== 04 - Drug Product Analysis Results ===")
    print(f"Total records: {len(df)}")

    # Check for non-empty values (not empty string and not NaN)
    molecules_count = len(df[(df['Molecule_MVS'].notna()) & (df['Molecule_MVS'] != '')])
    create_count = len(df[(df['Drug_Products_Loader_Create'].notna()) & (df['Drug_Products_Loader_Create'] != '')])
    update_count = len(df[(df['Drug_Products_Loader_Update'].notna()) & (df['Drug_Products_Loader_Update'] != '')])
    rim_count = len(df[(df['Drug_Product_Names_RIM'].notna()) & (df['Drug_Product_Names_RIM'] != '')])

    print(f"Records with molecules: {molecules_count}")
    print(f"Records with create chain: {create_count}")
    print(f"Records with update chain: {update_count}")
    print(f"Records with RIM chain: {rim_count}")

    print("\n=== Sample Records ===")
    print(df.head(5).to_string())

    print("\n=== Records with Multiple Drug Products ===")
    multi_create = df[df['Drug_Products_Loader_Create'].str.contains('\\|', na=False)]
    if not multi_create.empty:
        print("Create chain with multiple products:")
        print(multi_create[['MVS_Unique_ID', 'Drug_Products_Loader_Create']].head(3).to_string())

    multi_rim = df[df['Drug_Product_Names_RIM'].str.contains('\\|', na=False)]
    if not multi_rim.empty:
        print("\nRIM chain with multiple products:")
        print(multi_rim[['MVS_Unique_ID', 'Drug_Product_Names_RIM']].head(3).to_string())

    print("\n=== Data Quality Check ===")
    print("Unique values in each column:")
    for col in ['Drug_Products_Loader_Create', 'Drug_Products_Loader_Update', 'Drug_Product_Names_RIM']:
        unique_vals = df[col].value_counts().head(5)
        print(f"\n{col}:")
        print(unique_vals)

if __name__ == "__main__":
    main()
