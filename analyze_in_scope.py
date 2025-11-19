import pandas as pd
from collections import Counter

# Read the CSV file
df = pd.read_csv('.Archive VAL RUN/03 - Compare Unique IDs and Green Light.csv')

# Get all unique values in Out_of_Scope column
print('All unique Out_of_Scope values:')
out_of_scope_values = df['Out_of_Scope'].value_counts()
print(out_of_scope_values)
print('\n' + '='*70 + '\n')

# Find all variations that contain 'scope' and 'in' (case-insensitive)
in_scope_variations = []
for value in df['Out_of_Scope'].unique():
    if pd.notna(value):
        value_lower = str(value).lower()
        if 'in' in value_lower and 'scope' in value_lower and 'out' not in value_lower:
            in_scope_variations.append(str(value))

print('In Scope variations found:')
for var in sorted(in_scope_variations):
    count = len(df[df['Out_of_Scope'] == var])
    print(f'  - "{var}": {count} records')

print('\n' + '='*70 + '\n')

# Filter for all In Scope variations
in_scope_mask = df['Out_of_Scope'].isin(in_scope_variations)
in_scope_df = df[in_scope_mask]

# Count unique IDs
unique_in_scope_ids = in_scope_df['MVS_Unique_ID'].nunique()
total_in_scope_records = len(in_scope_df)

print(f'TOTAL UNIQUE IDs that are In Scope: {unique_in_scope_ids}')
print(f'Total records (with duplicates): {total_in_scope_records}')
