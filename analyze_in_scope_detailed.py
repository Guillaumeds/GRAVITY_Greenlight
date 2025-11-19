import pandas as pd

# Read the CSV file
df = pd.read_csv('.Archive VAL RUN/03 - Compare Unique IDs and Green Light.csv')

print('='*70)
print('IN SCOPE ANALYSIS - DETAILED REPORT')
print('='*70)
print()

# Find all variations that contain 'scope' and 'in' (case-insensitive)
in_scope_variations = []
for value in df['Out_of_Scope'].unique():
    if pd.notna(value):
        value_lower = str(value).lower()
        if 'in' in value_lower and 'scope' in value_lower and 'out' not in value_lower:
            in_scope_variations.append(str(value))

print('All "In Scope" variations found:')
print('-' * 70)
total_records = 0
for var in sorted(in_scope_variations):
    count = len(df[df['Out_of_Scope'] == var])
    total_records += count
    print(f'  "{var}": {count:,} records')

print('-' * 70)
print(f'  TOTAL: {total_records:,} records')
print()

# Filter for all In Scope variations
in_scope_mask = df['Out_of_Scope'].isin(in_scope_variations)
in_scope_df = df[in_scope_mask]

# Count unique IDs
unique_in_scope_ids = in_scope_df['MVS_Unique_ID'].nunique()

print('='*70)
print(f'TOTAL UNIQUE IDs that are "In Scope": {unique_in_scope_ids:,}')
print('='*70)
print()

# Additional breakdown
print('Additional Statistics:')
print('-' * 70)
print(f'  - Unique MVS IDs: {unique_in_scope_ids:,}')
print(f'  - Total records: {len(in_scope_df):,}')
print(f'  - Found in RIM: {len(in_scope_df[in_scope_df["Found_in_RIM"] == "Yes"]):,}')
print(f'  - NOT found in RIM: {len(in_scope_df[in_scope_df["Found_in_RIM"] == "No"]):,}')
print()

# Show sample of the variations
print('='*70)
print('SUMMARY OF "IN SCOPE" VARIATIONS FOUND:')
print('='*70)
for var in sorted(in_scope_variations):
    print(f'  • "{var}"')
print()
print(f'All {len(in_scope_variations)} variations have been included in the count.')
print('='*70)
