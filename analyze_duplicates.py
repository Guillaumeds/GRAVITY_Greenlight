import pandas as pd

# Read the CSV file
df = pd.read_csv('.Archive VAL RUN/03 - Compare Unique IDs and Green Light.csv')

print('='*70)
print('IN SCOPE - DUPLICATE ANALYSIS')
print('='*70)
print()

# Find all In Scope variations
in_scope_variations = []
for value in df['Out_of_Scope'].unique():
    if pd.notna(value):
        value_lower = str(value).lower()
        if 'in' in value_lower and 'scope' in value_lower and 'out' not in value_lower:
            in_scope_variations.append(str(value))

# Filter for all In Scope variations
in_scope_mask = df['Out_of_Scope'].isin(in_scope_variations)
in_scope_df = df[in_scope_mask]

print(f'Total "In Scope" records: {len(in_scope_df):,}')
print(f'Total UNIQUE MVS_Unique_IDs: {in_scope_df["MVS_Unique_ID"].nunique():,}')
print()

# Check for duplicates
duplicate_counts = in_scope_df['MVS_Unique_ID'].value_counts()
duplicates = duplicate_counts[duplicate_counts > 1]

if len(duplicates) > 0:
    print(f'IDs that appear MORE THAN ONCE: {len(duplicates):,}')
    print()
    print('Top 20 IDs with most duplicates:')
    print('-' * 70)
    for idx, (id_val, count) in enumerate(duplicates.head(20).items(), 1):
        print(f'  {idx}. {id_val}: appears {count} times')
    print()
else:
    print('No duplicates found - all IDs are unique!')
    print()

print('='*70)
print('SUMMARY:')
print('='*70)
print(f'  • Total records with "In Scope": {len(in_scope_df):,}')
print(f'  • Unique IDs (no duplicates): {in_scope_df["MVS_Unique_ID"].nunique():,}')
print(f'  • IDs appearing multiple times: {len(duplicates):,}')
print('='*70)
