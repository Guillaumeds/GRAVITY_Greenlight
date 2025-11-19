#!/usr/bin/env python3
"""
Analyze the matching issue between MVS and LoV data
"""

import pandas as pd
from rapidfuzz import fuzz

def analyze_matching():
    print("=" * 70)
    print("ANALYZING MATCHING ISSUES")
    print("=" * 70)
    
    # Load sample data
    df = pd.read_csv("03 - Compare Unique IDs and Green Light.csv", nrows=20)
    lov_df = pd.read_excel("04 Transformation Maps/LoV Object Mapping.xlsx")
    
    # Create MVS_Drug_Product
    df['MVS_Drug_Product'] = df['MVS_Dosage_Form'].astype(str) + " " + df['MVS_Molecule'].astype(str)
    
    # Get unique MVS products
    mvs_products = df['MVS_Drug_Product'].unique()[:5]
    
    # Get LoV source values
    lov_sources = lov_df['Source Value'].dropna().unique()[:20]
    
    print("Sample MVS Drug Products:")
    for i, mvs in enumerate(mvs_products):
        print(f"  {i+1}: {mvs}")
    
    print("\nSample LoV Source Values:")
    for i, lov in enumerate(lov_sources):
        print(f"  {i+1}: {lov}")
    
    print("\n" + "=" * 70)
    print("TESTING FUZZY MATCHING")
    print("=" * 70)
    
    # Test matching
    for mvs in mvs_products[:3]:
        print(f"\nMVS: '{mvs}'")
        best_matches = []
        
        for lov in lov_sources:
            score = fuzz.ratio(mvs, lov)
            if score > 30:  # Only show decent matches
                best_matches.append((lov, score))
        
        # Sort by score
        best_matches.sort(key=lambda x: x[1], reverse=True)
        
        print("  Best matches:")
        for lov, score in best_matches[:5]:
            print(f"    {score:.1f}% - {lov}")
        
        if not best_matches:
            print("    No matches above 30%")
    
    # Test partial matching (just molecule names)
    print("\n" + "=" * 70)
    print("TESTING PARTIAL MATCHING (MOLECULE ONLY)")
    print("=" * 70)
    
    molecules = df['MVS_Molecule'].unique()[:5]
    
    for mol in molecules:
        print(f"\nMolecule: '{mol}'")
        best_matches = []
        
        for lov in lov_sources:
            score = fuzz.ratio(mol, lov)
            if score > 50:
                best_matches.append((lov, score))
        
        best_matches.sort(key=lambda x: x[1], reverse=True)
        
        print("  Best matches:")
        for lov, score in best_matches[:3]:
            print(f"    {score:.1f}% - {lov}")
        
        if not best_matches:
            print("    No matches above 50%")

if __name__ == "__main__":
    analyze_matching()
