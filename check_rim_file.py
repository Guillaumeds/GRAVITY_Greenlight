import pandas as pd

df = pd.read_csv('03 Target RIM/regulatory_objective_rim.csv')
print(f'Rows: {len(df)}')
print(f'Has external_id__v: {"external_id__v" in df.columns}')
print(f'Non-null external_id__v: {df["external_id__v"].notna().sum()}')
print(f'\nSample values:')
print(df["external_id__v"].head(20))
print(f'\nValue counts (first 10):')
print(df["external_id__v"].value_counts().head(10))
