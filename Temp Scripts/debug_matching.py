#!/usr/bin/env python3
"""
Debug the matching issue
"""

import pandas as pd
from rapidfuzz import fuzz, process

def debug_matching():
    print("=" * 50)
    print("DEBUG MATCHING")
    print("=" * 50)
    
    # Load RIM products
    product_df = pd.read_csv("03 Target RIM/product__v_data.csv")
    rim_products = product_df['name__v'].dropna()
    rim_choices = rim_products.astype(str).str.strip().unique().tolist()
    
    print(f"RIM product choices: {len(rim_choices)}")
    print("First 10 RIM products:")
    for i, prod in enumerate(rim_choices[:10]):
        print(f"  {i+1}: {prod}")
    
    # Test MVS molecules
    mvs_molecules = ["Levothyroxine sodium", "Remifentanil Hydrochloride", "Atracurium Besylate"]
    
    print(f"\nTesting MVS molecules:")
    for mvs_mol in mvs_molecules:
        print(f"\nMVS_Molecule: '{mvs_mol}'")
        
        # Find best match
        best_match = process.extractOne(
            mvs_mol, 
            rim_choices, 
            scorer=fuzz.ratio, 
            score_cutoff=75
        )
        
        if best_match:
            matched_product, score = best_match[0], best_match[1]
            print(f"  -> MATCH: '{matched_product}' (Score: {score:.1f}%)")
        else:
            print(f"  -> NO MATCH above 75%")
            
            # Show top 5 matches regardless of threshold
            top_matches = process.extract(mvs_mol, rim_choices, scorer=fuzz.ratio, limit=5)
            print(f"  Top 5 matches:")
            for match, score in top_matches:
                print(f"    {score:.1f}% - {match}")

if __name__ == "__main__":
    debug_matching()
