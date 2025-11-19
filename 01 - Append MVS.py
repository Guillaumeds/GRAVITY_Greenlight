#!/usr/bin/env python3
"""
01 - Append MVS Script
Appends all Excel files from the MVS source folder into a single CSV file.
Generates a quality report showing file counts and any issues.
"""

import pandas as pd
import pathlib
import datetime
import sys
from typing import List, Dict, Tuple


def get_excel_files(source_dir: pathlib.Path) -> List[pathlib.Path]:
    """Find all Excel files in the source directory (root level only)."""
    excel_files = []
    for pattern in ['*.xlsx', '*.xls']:
        excel_files.extend(source_dir.glob(pattern))
    return sorted(excel_files)


def read_excel_file(file_path: pathlib.Path) -> Tuple[pd.DataFrame, Dict]:
    """Read an Excel file and return DataFrame with metadata."""
    metadata = {
        'filename': file_path.name,
        'row_count': 0,
        'column_count': 0,
        'columns': []
    }

    print(f"Reading: {file_path.name}")
    df = pd.read_excel(file_path, skiprows=1)

    if df.empty:
        print(f"❌ ERROR: File is empty: {file_path.name}")
        sys.exit(1)

    metadata['row_count'] = len(df)
    metadata['column_count'] = len(df.columns)
    metadata['columns'] = list(df.columns)

    return df, metadata


def write_with_retry(df: pd.DataFrame, output_path: pathlib.Path):
    """Write CSV with file lock handling and retry mechanism."""
    while True:
        try:
            print(f"Writing to: {output_path}")
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"  SUCCESS: Successfully written {len(df)} rows")
            return

        except PermissionError:
            print(f"  ERROR: File is locked: {output_path}")
            print(f"  Please close the file in Excel and press Enter to retry...")
            input("  Press Enter when ready: ")
            continue

        except Exception:
            print(f"ERROR: Could not write file: {output_path}")
            sys.exit(1)


def create_quality_report(file_stats: List[Dict], total_rows: int, report_path: pathlib.Path):
    """Generate a quality report with statistics and issues."""

    with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("MVS FILES APPEND QUALITY REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            successful_files = [s for s in file_stats if s['row_count'] > 0]
            sum_individual_rows = sum(s['row_count'] for s in successful_files)

            f.write("SUMMARY:\n")
            f.write(f"  Total files found: {len(file_stats)}\n")
            f.write(f"  Successfully processed: {len(successful_files)}\n")
            f.write(f"  Sum of individual file rows: {sum_individual_rows:,}\n")
            f.write(f"  Total rows in appended file: {total_rows:,}\n")

            # Row count validation
            if sum_individual_rows == total_rows:
                f.write(f"  SUCCESS: Row count validation: PASSED (no data loss/duplication)\n")
            else:
                difference = total_rows - sum_individual_rows
                if difference > 0:
                    f.write(f"  WARNING: Row count validation: FAILED (+{difference:,} extra rows - possible duplication)\n")
                else:
                    f.write(f"  ERROR: Row count validation: FAILED ({difference:,} missing rows - data loss detected)\n")
            f.write("\n")
            
            # File details
            f.write("FILE DETAILS:\n")
            f.write("-" * 60 + "\n")
            for stat in file_stats:
                f.write(f"File: {stat['filename']}\n")
                f.write(f"  Rows: {stat['row_count']:,}\n")
                f.write(f"  Columns: {stat['column_count']}\n")
                f.write("\n")
            
            # Column analysis
            if successful_files:
                all_columns = set()
                for stat in successful_files:
                    all_columns.update(stat['columns'])
                
                f.write("COLUMN ANALYSIS:\n")
                f.write("-" * 60 + "\n")
                f.write(f"Total unique columns found: {len(all_columns)}\n")
                f.write("Columns: " + ", ".join(sorted(all_columns)) + "\n\n")
            

        
    print(f"  SUCCESS: Quality report saved: {report_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("MVS FILES APPEND SCRIPT")
    print("=" * 60)
    
    # Define paths
    source_dir = pathlib.Path("01 Source MVS")
    output_file = pathlib.Path("01 - Append MVS.csv")
    quality_report_file = pathlib.Path("01 - Append MVS - Quality.txt")
    
    # Validate source directory
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)
    
    print(f"Output files will be saved in root directory")
    
    # Find Excel files
    excel_files = get_excel_files(source_dir)
    if not excel_files:
        print("❌ No Excel files found in source directory")
        sys.exit(1)
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process files
    all_dataframes = []
    file_stats = []

    for file_path in excel_files:
        df, metadata = read_excel_file(file_path)
        file_stats.append(metadata)
        all_dataframes.append(df)

    # Combine all dataframes
    if not all_dataframes:
        print("❌ ERROR: No valid data found in any files")
        sys.exit(1)
    
    print(f"\nCombining {len(all_dataframes)} dataframes...")
    combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
    
    # Write output
    write_with_retry(combined_df, output_file)
    
    # Generate quality report
    create_quality_report(file_stats, len(combined_df), quality_report_file)
    
    print("\n" + "=" * 60)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print(f"Output file: {output_file}")
    print(f"Quality report: {quality_report_file}")
    print(f"Total rows: {len(combined_df):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
