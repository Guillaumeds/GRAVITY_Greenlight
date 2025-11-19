"""
Purpose: Expand regulatory_objective__rim.csv with registration information through multi-table merges
Process: Load regulatory objectives, merge with registration relationships, then merge with registration details
Success Criteria: Output CSV contains all original regulatory objective data plus registration_number, registration_number__rim, state__v, and maintain_registration__c
Logic: Left outer merge regulatory_objective__rim -> registration_regulatory_objective__rim -> registration__rim
"""

import pandas as pd
import sys

def main():
    try:
        # Load source files with UTF-8 encoding
        print("Loading regulatory_objective__rim.csv...")
        regulatory_obj = pd.read_csv(r"02 Loader sheets\regulatory_objective__rim.csv", encoding='utf-8')
        
        print("Loading registration_regulatory_objective__rim.csv...")
        reg_reg_obj = pd.read_csv(r"02 Loader sheets\registration_regulatory_objective__rim.csv", encoding='utf-8')
        
        print("Loading registration__rim.csv...")
        registrations = pd.read_csv(r"C:\00 GRAVITY\01 RIM and MVS DBs (Extract and Enrich)\output\RIM PROD RAW\registration__rim.csv", encoding='utf-8')
        
        # First merge: regulatory_objective__rim with registration_regulatory_objective__rim
        print("Performing first merge: regulatory objectives with registration relationships...")
        merged_step1 = pd.merge(
            regulatory_obj,
            reg_reg_obj,
            left_on='external_id__v',
            right_on='regulatory_objective__rim',
            how='left'
        )
        
        # Second merge: result with registration__rim
        print("Performing second merge: adding registration details...")
        final_result = pd.merge(
            merged_step1,
            registrations[['id', 'registration_number__rim', 'state__v', 'maintain_registration__c']],
            left_on='registration_number',
            right_on='id',
            how='left'
        )
        
        # Save result with UTF-8 encoding
        output_file = "08 - Create Loader with REG Info.csv"
        print(f"Saving expanded loader sheet to {output_file}...")
        final_result.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"SUCCESS: Created {output_file}")
        print(f"Original records: {len(regulatory_obj)}")
        print(f"Final records: {len(final_result)}")
        print(f"Records with registration info: {final_result['registration_number'].notna().sum()}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
