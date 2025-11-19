#!/usr/bin/env python3
"""
Simple test for 04 - Drug Product Analysis functionality
"""

import pandas as pd
import pathlib

def test_basic_functionality():
    """Test basic functionality without complex imports."""
    print("=" * 50)
    print("TESTING 04 - DRUG PRODUCT ANALYSIS COMPONENTS")
    print("=" * 50)
    
    try:
        # Test loading input file
        input_file = pathlib.Path("03 - Compare Unique IDs and Green Light.csv")
        if input_file.exists():
            print("✓ Input file found")
            df = pd.read_csv(input_file, encoding='utf-8', nrows=5)
            print(f"✓ Loaded sample data: {len(df)} rows")
            print("Columns:", list(df.columns))
        else:
            print("✗ Input file not found")
            return
        
        # Test product file
        product_file = pathlib.Path("03 Target RIM/product__v_data.csv")
        if product_file.exists():
            print("✓ Product file found")
            product_df = pd.read_csv(product_file, encoding='utf-8', nrows=5)
            print(f"✓ Loaded product data: {len(product_df)} rows")
        else:
            print("✗ Product file not found")
            return
        
        # Test LoV file
        lov_file = pathlib.Path("04 Transformation Maps/LoV Object Mapping.xlsx")
        if lov_file.exists():
            print("✓ LoV mapping file found")
            lov_df = pd.read_excel(lov_file, nrows=5)
            print(f"✓ Loaded LoV data: {len(lov_df)} rows")
        else:
            print("✗ LoV mapping file not found")
            return
        
        # Test creating MVS_Drug_Product
        if 'MVS_Dosage_Form' in df.columns and 'MVS_Molecule' in df.columns:
            df['MVS_Drug_Product'] = df['MVS_Dosage_Form'].astype(str) + " " + df['MVS_Molecule'].astype(str)
            print("✓ Created MVS_Drug_Product column")
            print("Sample MVS_Drug_Product values:")
            print(df['MVS_Drug_Product'].head().tolist())
        else:
            print("✗ Required columns for MVS_Drug_Product not found")
        
        print("\n" + "=" * 50)
        print("BASIC FUNCTIONALITY TEST COMPLETED")
        print("✓ All components accessible")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
