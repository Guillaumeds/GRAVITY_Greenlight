#!/usr/bin/env python3
"""
Find actual matches between MVS and LoV data
"""

import pandas as pd
from rapidfuzz import fuzz

def find_actual_matches():
    print("=" * 70)
    print("FINDING ACTUAL MATCHES")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv("03 - Compare Unique IDs and Green Light.csv")
    lov_df = pd.read_excel("04 Transformation Maps/LoV Object Mapping.xlsx")
    
    # Get unique molecules and LoV sources
    mvs_molecules = df['MVS_Molecule'].dropna().unique()
    lov_sources = lov_df['Source Value'].dropna().astype(str).unique()
    
    print(f"Total MVS Molecules: {len(mvs_molecules)}")
    print(f"Total LoV Sources: {len(lov_sources)}")
    
    print("\nMVS Molecules (first 20):")
    for i, mol in enumerate(mvs_molecules[:20]):
        print(f"  {i+1}: {mol}")
    
    print("\nLoV Sources (first 20):")
    for i, lov in enumerate(lov_sources[:20]):
        print(f"  {i+1}: {lov}")
    
    # Find potential matches by checking if any MVS molecule words appear in LoV
    print("\n" + "=" * 70)
    print("SEARCHING FOR WORD OVERLAPS")
    print("=" * 70)
    
    potential_matches = []
    
    for mvs_mol in mvs_molecules:
        mvs_words = [word.lower().strip() for word in str(mvs_mol).split() if len(word) > 3]
        
        for lov_source in lov_sources:
            lov_lower = str(lov_source).lower()
            
            # Check if any significant word from MVS appears in LoV
            for word in mvs_words:
                if word in lov_lower:
                    score = fuzz.ratio(mvs_mol, lov_source)
                    potential_matches.append((mvs_mol, lov_source, word, score))
                    break
    
    print(f"Found {len(potential_matches)} potential word overlaps")
    
    # Sort by score
    potential_matches.sort(key=lambda x: x[3], reverse=True)
    
    print("\nTop 20 potential matches:")
    for mvs, lov, word, score in potential_matches[:20]:
        print(f"  {score:.1f}% - '{mvs}' -> '{lov}' (word: {word})")
    
    # Test with lower thresholds
    print("\n" + "=" * 70)
    print("TESTING WITH LOWER THRESHOLDS")
    print("=" * 70)
    
    thresholds = [70, 60, 50, 40]
    
    for threshold in thresholds:
        matches = [m for m in potential_matches if m[3] >= threshold]
        print(f"Matches at {threshold}% threshold: {len(matches)}")
        
        if matches:
            print(f"  Top 5 at {threshold}%:")
            for mvs, lov, word, score in matches[:5]:
                print(f"    {score:.1f}% - '{mvs}' -> '{lov}'")
    
    # Check if the issue is with the matching strategy
    print("\n" + "=" * 70)
    print("TESTING DIFFERENT MATCHING STRATEGIES")
    print("=" * 70)
    
    # Test partial ratio
    sample_mvs = mvs_molecules[0]
    sample_lov = lov_sources[0]
    
    print(f"Sample MVS: '{sample_mvs}'")
    print(f"Sample LoV: '{sample_lov}'")
    print(f"  fuzz.ratio: {fuzz.ratio(sample_mvs, sample_lov):.1f}%")
    print(f"  fuzz.partial_ratio: {fuzz.partial_ratio(sample_mvs, sample_lov):.1f}%")
    print(f"  fuzz.token_sort_ratio: {fuzz.token_sort_ratio(sample_mvs, sample_lov):.1f}%")
    print(f"  fuzz.token_set_ratio: {fuzz.token_set_ratio(sample_mvs, sample_lov):.1f}%")

if __name__ == "__main__":
    find_actual_matches()
