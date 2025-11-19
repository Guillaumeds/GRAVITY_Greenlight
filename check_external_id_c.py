import pandas as pd

df = pd.read_csv('03 Target RIM/regulatory_objective_rim.csv')
print(f'Has external_id__c: {"external_id__c" in df.columns}')
if "external_id__c" in df.columns:
    print(f'Non-null external_id__c: {df["external_id__c"].notna().sum()}')
    print(f'\nSample values:')
    print(df[df["external_id__c"].notna()]["external_id__c"].head(20))
else:
    print('external_id__c column not found')
