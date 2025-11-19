#!/usr/bin/env python3
"""
06 - Analyse joins in RIM Script
Analyzes joins in RIM for created and updated ROs during migration.
Creates separate outputs for created and updated RO join analysis.
"""

import pandas as pd
import pathlib
import sys
from datetime import datetime
import migration_config


def parse_rim_date(date_str):
    """Parse RIM date string to datetime object."""
    if pd.isna(date_str) or not str(date_str).strip():
        return None
    
    try:
        # Handle RIM ISO format: 2025-09-12T16:38:00.000Z
        date_str = str(date_str).strip()
        if date_str.endswith('Z'):
            date_str = date_str[:-1]  # Remove Z
        if '.' in date_str:
            date_str = date_str.split('.')[0]  # Remove milliseconds
        
        return datetime.fromisoformat(date_str)
    except:
        return None


def is_in_migration_range(date_obj, start_date_str, end_date_str):
    """Check if date is within migration range."""
    if date_obj is None:
        return False
    
    start_date = parse_rim_date(start_date_str)
    end_date = parse_rim_date(end_date_str)
    
    if start_date is None or end_date is None:
        return False
    
    return start_date <= date_obj <= end_date


def is_before_migration_start(date_obj, start_date_str):
    """Check if date is before migration start."""
    if date_obj is None:
        return False
    
    start_date = parse_rim_date(start_date_str)
    if start_date is None:
        return False
    
    return date_obj < start_date


def load_join_files():
    """Load the join files for analysis."""
    print("Loading join files...")
    
    # Load registration_regulatory_objective file
    reg_file = pathlib.Path("03 Target RIM/registration_regulatory_objective__rim_data.csv")
    if not reg_file.exists():
        print(f"ERROR: Registration join file not found: {reg_file}")
        sys.exit(1)
    
    df_reg = pd.read_csv(reg_file, encoding='utf-8')
    if 'regulatory_objective__rim' not in df_reg.columns:
        print("ERROR: 'regulatory_objective__rim' column not found in registration join file")
        sys.exit(1)
    
    # Load drug_product join file
    drug_file = pathlib.Path("03 Target RIM/regulatory_objective_drug_product__v_data.csv")
    if not drug_file.exists():
        print(f"ERROR: Drug product join file not found: {drug_file}")
        sys.exit(1)
    
    df_drug = pd.read_csv(drug_file, encoding='utf-8')
    if 'regulatory_objective__v' not in df_drug.columns:
        print("ERROR: 'regulatory_objective__v' column not found in drug product join file")
        sys.exit(1)
    
    print(f"  Loaded registration joins: {len(df_reg)} rows")
    print(f"  Loaded drug product joins: {len(df_drug)} rows")
    
    return df_reg, df_drug


def count_joins(target_id, df, column_name):
    """Count how many times an ID appears in a join file column."""
    if pd.isna(target_id) or not str(target_id).strip():
        return 0
    
    target_id_str = str(target_id).strip()
    count = 0
    
    for value in df[column_name]:
        if pd.notna(value) and str(value).strip() == target_id_str:
            count += 1
    
    return count


def analyze_created_ros():
    """Analyze joins for created ROs (created & modified in migration range)."""
    print("Analyzing joins for created ROs...")
    
    # Load RIM data
    rim_file = pathlib.Path(migration_config.RIM_FILTERED_FILE)
    if not rim_file.exists():
        print(f"ERROR: RIM file not found: {rim_file}")
        sys.exit(1)
    
    df_rim = pd.read_csv(rim_file, encoding='utf-8')
    
    created_col, modified_col = migration_config.get_rim_date_columns()
    start_date, end_date = migration_config.get_migration_date_range()
    
    # Validate columns
    required_cols = [created_col, modified_col, 'external_id__c', 'id']
    for col in required_cols:
        if col not in df_rim.columns:
            print(f"ERROR: '{col}' column not found in RIM file")
            sys.exit(1)
    
    # Load join files
    df_reg, df_drug = load_join_files()
    
    # Filter for created ROs (both created and modified in migration range)
    created_ros = []
    
    for _, row in df_rim.iterrows():
        created_date = parse_rim_date(row[created_col])
        modified_date = parse_rim_date(row[modified_col])
        
        if (is_in_migration_range(created_date, start_date, end_date) and 
            is_in_migration_range(modified_date, start_date, end_date)):
            
            external_id = row['external_id__c']
            ro_id = row['id']
            
            # Count joins
            reg_joins = count_joins(ro_id, df_reg, 'regulatory_objective__rim')
            drug_joins = count_joins(ro_id, df_drug, 'regulatory_objective__v')
            
            created_ros.append({
                'External_ID': str(external_id).strip() if pd.notna(external_id) else '',
                'Registration_Joins': reg_joins,
                'Drug_Product_Joins': drug_joins
            })
    
    print(f"  Found {len(created_ros)} created ROs")
    return created_ros


def analyze_updated_ros():
    """Analyze joins for updated ROs (modified in range, created before range)."""
    print("Analyzing joins for updated ROs...")
    
    # Load RIM data
    rim_file = pathlib.Path(migration_config.RIM_FILTERED_FILE)
    df_rim = pd.read_csv(rim_file, encoding='utf-8')
    
    created_col, modified_col = migration_config.get_rim_date_columns()
    start_date, end_date = migration_config.get_migration_date_range()
    
    # Load join files
    df_reg, df_drug = load_join_files()
    
    # Filter for updated ROs (modified in range, created before range)
    updated_ros = []
    
    for _, row in df_rim.iterrows():
        created_date = parse_rim_date(row[created_col])
        modified_date = parse_rim_date(row[modified_col])
        
        if (is_in_migration_range(modified_date, start_date, end_date) and 
            is_before_migration_start(created_date, start_date)):
            
            external_id = row['external_id__c']
            ro_id = row['id']
            
            # Count total joins in drug product file
            total_drug_joins = count_joins(ro_id, df_drug, 'regulatory_objective__v')
            
            # Count joins in drug product file that were created before mig and modified during mig
            filtered_drug_joins = 0
            for _, drug_row in df_drug.iterrows():
                if (pd.notna(drug_row['regulatory_objective__v']) and 
                    str(drug_row['regulatory_objective__v']).strip() == str(ro_id).strip()):
                    
                    drug_created = parse_rim_date(drug_row['created_date__v'])
                    drug_modified = parse_rim_date(drug_row['modified_date__v'])
                    
                    if (is_before_migration_start(drug_created, start_date) and 
                        is_in_migration_range(drug_modified, start_date, end_date)):
                        filtered_drug_joins += 1
            
            updated_ros.append({
                'External_ID': str(external_id).strip() if pd.notna(external_id) else '',
                'Total_Drug_Product_Joins': total_drug_joins,
                'Filtered_Drug_Product_Joins': filtered_drug_joins
            })
    
    print(f"  Found {len(updated_ros)} updated ROs")
    return updated_ros


def export_results(results, output_file, analysis_type):
    """Export results to CSV file with file lock handling."""
    print(f"Exporting {analysis_type} results to: {output_file}")
    
    if not results:
        print(f"  No {analysis_type} data to export")
        return
    
    results_df = pd.DataFrame(results)
    
    # Handle file lock with retry mechanism
    while True:
        try:
            results_df.to_csv(output_file, index=False, encoding='utf-8')
            break
        except PermissionError:
            print(f"ERROR: File is locked: {output_file}")
            print("Please close the file in Excel and press Enter to retry...")
            input("Press Enter when ready: ")
            continue
        except Exception:
            print(f"ERROR: Could not write file: {output_file}")
            sys.exit(1)
    
    print(f"  SUCCESS: Exported {len(results)} {analysis_type} records")


def main():
    """Main execution function."""
    print("=" * 70)
    print("RIM JOINS ANALYSIS")
    print("=" * 70)
    
    start_date, end_date = migration_config.get_migration_date_range()
    print(f"Migration date range: {start_date} to {end_date}")
    print()
    
    # Analyze created ROs
    created_results = analyze_created_ros()
    created_output = pathlib.Path("06 - Analyse joins in RIM - Joins for created ROs.csv")
    export_results(created_results, created_output, "created RO")
    
    print()
    
    # Analyze updated ROs
    updated_results = analyze_updated_ros()
    updated_output = pathlib.Path("06 - Analyse joins in RIM - Joins for updated ROs.csv")
    export_results(updated_results, updated_output, "updated RO")
    
    print("\n" + "=" * 70)
    print("RIM JOINS ANALYSIS COMPLETED SUCCESSFULLY")
    print(f"Created ROs output: {created_output}")
    print(f"Updated ROs output: {updated_output}")
    print("=" * 70)


if __name__ == "__main__":
    main()
