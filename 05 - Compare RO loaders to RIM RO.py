#!/usr/bin/env python3
"""
05 - Compare RO loaders to RIM RO Script
Compares RO loader expectations with actual RIM RO creation and updates.
Analyzes counts, non-null records, and unique ID permutations across systems.
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


def analyze_loader_create_expected():
    """Analyze RO expected to be created from loader create file."""
    print("Analyzing RO expected to be created (Loader Create)...")

    file_path = pathlib.Path(migration_config.LOADER_CREATE_FILE)
    if not file_path.exists():
        print(f"ERROR: Loader Create file not found: {file_path}")
        sys.exit(1)

    df = pd.read_csv(file_path, encoding='utf-8')

    if 'external_id__v' not in df.columns:
        print("ERROR: 'external_id__v' column not found in Loader Create file")
        sys.exit(1)

    total_rows = len(df)
    non_null_ids = df['external_id__v'].notna().sum()
    non_empty_ids = len([x for x in df['external_id__v'] if pd.notna(x) and str(x).strip()])
    unique_ids = len(df['external_id__v'].dropna().astype(str).str.strip().unique())

    # Collect expected create IDs for discrepancy analysis
    expected_create_ids = set()
    for value in df['external_id__v']:
        if pd.notna(value) and str(value).strip():
            expected_create_ids.add(str(value).strip())

    print(f"  Total rows: {total_rows}")
    print(f"  Non-null/empty IDs: {non_empty_ids}")
    print(f"  Unique ID permutations: {unique_ids}")

    return {
        'Create_Expected_Total_Rows': total_rows,
        'Create_Expected_NonNull_IDs': non_empty_ids,
        'Create_Expected_Unique_IDs': unique_ids,
        'expected_create_ids': expected_create_ids
    }


def analyze_rim_created():
    """Analyze RO actually created in RIM (both created and modified in migration range)."""
    print("Analyzing RO created in RIM (created & modified in migration range)...")

    file_path = pathlib.Path(migration_config.RIM_FILTERED_FILE)
    if not file_path.exists():
        print(f"ERROR: RIM file not found: {file_path}")
        sys.exit(1)

    df = pd.read_csv(file_path, encoding='utf-8')

    created_col, modified_col = migration_config.get_rim_date_columns()
    start_date, end_date = migration_config.get_migration_date_range()

    if created_col not in df.columns:
        print(f"ERROR: '{created_col}' column not found in RIM file")
        sys.exit(1)

    if modified_col not in df.columns:
        print(f"ERROR: '{modified_col}' column not found in RIM file")
        sys.exit(1)

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in RIM file")
        sys.exit(1)

    # Filter for records where both created and modified dates are in migration range
    filtered_rows = []
    rim_created_ids = set()

    for _, row in df.iterrows():
        created_date = parse_rim_date(row[created_col])
        modified_date = parse_rim_date(row[modified_col])

        if (is_in_migration_range(created_date, start_date, end_date) and
            is_in_migration_range(modified_date, start_date, end_date)):
            filtered_rows.append(row)
            # Collect IDs for discrepancy analysis
            if pd.notna(row['external_id__c']) and str(row['external_id__c']).strip():
                rim_created_ids.add(str(row['external_id__c']).strip())

    if filtered_rows:
        filtered_df = pd.DataFrame(filtered_rows)
        total_rows = len(filtered_df)
        non_empty_ids = len([x for x in filtered_df['external_id__c'] if pd.notna(x) and str(x).strip()])
        unique_ids = len(filtered_df['external_id__c'].dropna().astype(str).str.strip().unique())
    else:
        total_rows = 0
        non_empty_ids = 0
        unique_ids = 0

    print(f"  Total rows (created & modified in range): {total_rows}")
    print(f"  Non-null/empty IDs: {non_empty_ids}")
    print(f"  Unique ID permutations: {unique_ids}")

    return {
        'RIM_Created_Total_Rows': total_rows,
        'RIM_Created_NonNull_IDs': non_empty_ids,
        'RIM_Created_Unique_IDs': unique_ids,
        'rim_created_ids': rim_created_ids
    }


def analyze_loader_update_expected():
    """Analyze RO expected to be updated from loader update file."""
    print("Analyzing RO expected to be updated (Loader Update)...")

    file_path = pathlib.Path(migration_config.LOADER_UPDATE_FILE)
    if not file_path.exists():
        print(f"ERROR: Loader Update file not found: {file_path}")
        sys.exit(1)

    df = pd.read_csv(file_path, encoding='utf-8')

    if 'external_id__c' not in df.columns:
        print("ERROR: 'external_id__c' column not found in Loader Update file")
        sys.exit(1)

    total_rows = len(df)
    non_empty_ids = len([x for x in df['external_id__c'] if pd.notna(x) and str(x).strip()])
    unique_ids = len(df['external_id__c'].dropna().astype(str).str.strip().unique())

    # Collect expected update IDs for discrepancy analysis
    expected_update_ids = set()
    for value in df['external_id__c']:
        if pd.notna(value) and str(value).strip():
            expected_update_ids.add(str(value).strip())

    print(f"  Total rows: {total_rows}")
    print(f"  Non-null/empty IDs: {non_empty_ids}")
    print(f"  Unique ID permutations: {unique_ids}")

    return {
        'Update_Expected_Total_Rows': total_rows,
        'Update_Expected_NonNull_IDs': non_empty_ids,
        'Update_Expected_Unique_IDs': unique_ids,
        'expected_update_ids': expected_update_ids
    }


def analyze_rim_updated():
    """Analyze RO actually updated in RIM (modified in range, created before range)."""
    print("Analyzing RO updated in RIM (modified in range, created before range)...")

    file_path = pathlib.Path(migration_config.RIM_FILTERED_FILE)
    if not file_path.exists():
        print(f"ERROR: RIM file not found: {file_path}")
        sys.exit(1)

    df = pd.read_csv(file_path, encoding='utf-8')

    created_col, modified_col = migration_config.get_rim_date_columns()
    start_date, end_date = migration_config.get_migration_date_range()

    # Filter for records where modified is in range but created is before range
    filtered_rows = []
    rim_updated_ids = set()

    for _, row in df.iterrows():
        created_date = parse_rim_date(row[created_col])
        modified_date = parse_rim_date(row[modified_col])

        if (is_in_migration_range(modified_date, start_date, end_date) and
            is_before_migration_start(created_date, start_date)):
            filtered_rows.append(row)
            # Collect IDs for discrepancy analysis
            if pd.notna(row['external_id__c']) and str(row['external_id__c']).strip():
                rim_updated_ids.add(str(row['external_id__c']).strip())

    if filtered_rows:
        filtered_df = pd.DataFrame(filtered_rows)
        total_rows = len(filtered_df)
        non_empty_ids = len([x for x in filtered_df['external_id__c'] if pd.notna(x) and str(x).strip()])
        unique_ids = len(filtered_df['external_id__c'].dropna().astype(str).str.strip().unique())
    else:
        total_rows = 0
        non_empty_ids = 0
        unique_ids = 0

    print(f"  Total rows (modified in range, created before): {total_rows}")
    print(f"  Non-null/empty IDs: {non_empty_ids}")
    print(f"  Unique ID permutations: {unique_ids}")

    return {
        'RIM_Updated_Total_Rows': total_rows,
        'RIM_Updated_NonNull_IDs': non_empty_ids,
        'RIM_Updated_Unique_IDs': unique_ids,
        'rim_updated_ids': rim_updated_ids
    }


def analyze_create_discrepancies(expected_create_ids: set, rim_created_ids: set) -> str:
    """Analyze discrepancies between expected create and actual RIM created."""
    print("Analyzing create discrepancies...")

    # Find IDs expected but not created
    expected_not_created = expected_create_ids - rim_created_ids
    # Find IDs created but not expected
    created_not_expected = rim_created_ids - expected_create_ids

    discrepancies = []

    if expected_not_created:
        discrepancies.append(f"Expected but not created: {', '.join(sorted(expected_not_created))}")

    if created_not_expected:
        discrepancies.append(f"Created but not expected: {', '.join(sorted(created_not_expected))}")

    discrepancy_text = " | ".join(discrepancies) if discrepancies else ""

    print(f"  Expected not created: {len(expected_not_created)}")
    print(f"  Created not expected: {len(created_not_expected)}")

    return discrepancy_text


def analyze_update_discrepancies(expected_update_ids: set, rim_updated_ids: set) -> str:
    """Analyze discrepancies between expected update and actual RIM updated."""
    print("Analyzing update discrepancies...")

    # Find IDs expected but not updated
    expected_not_updated = expected_update_ids - rim_updated_ids
    # Find IDs updated but not expected
    updated_not_expected = rim_updated_ids - expected_update_ids

    discrepancies = []

    if expected_not_updated:
        discrepancies.append(f"Expected but not updated: {', '.join(sorted(expected_not_updated))}")

    if updated_not_expected:
        discrepancies.append(f"Updated but not expected: {', '.join(sorted(updated_not_expected))}")

    discrepancy_text = " | ".join(discrepancies) if discrepancies else ""

    print(f"  Expected not updated: {len(expected_not_updated)}")
    print(f"  Updated not expected: {len(updated_not_expected)}")

    return discrepancy_text


def export_results(results: dict, output_file: pathlib.Path):
    """Export results to CSV file with file lock handling."""
    print(f"Exporting results to: {output_file}")
    
    # Create single row with all results
    results_df = pd.DataFrame([results])
    
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
    
    print(f"  SUCCESS: Exported comparison analysis")


def main():
    """Main execution function."""
    print("=" * 70)
    print("RO LOADERS TO RIM RO COMPARISON ANALYSIS")
    print("=" * 70)
    
    start_date, end_date = migration_config.get_migration_date_range()
    print(f"Migration date range: {start_date} to {end_date}")
    print()
    
    # Perform all analyses
    create_expected = analyze_loader_create_expected()
    rim_created = analyze_rim_created()
    update_expected = analyze_loader_update_expected()
    rim_updated = analyze_rim_updated()
    
    # Combine all results
    all_results = {**create_expected, **rim_created, **update_expected, **rim_updated}
    
    # Export results
    output_file = pathlib.Path("05 - Compare RO loaders to RIM RO.csv")
    export_results(all_results, output_file)
    
    print("\n" + "=" * 70)
    print("RO LOADERS TO RIM RO COMPARISON COMPLETED SUCCESSFULLY")
    print(f"Output file: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
