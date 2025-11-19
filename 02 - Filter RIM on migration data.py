#!/usr/bin/env python3
"""
02 - Filter RIM on Migration Data Script
Filters regulatory_objective__rim_data.csv based on modified_date__v column within specified date range.
Places filtered results in MIG Filtered folder.
"""

import pandas as pd
import pathlib
import datetime
import sys
from typing import Dict, Optional

# ============================================================================
# CONFIGURATION - Edit these dates as needed
# Format: YYYY-MM-DDTHH:MM:SS.000Z (example: 2025-09-12T16:38:00.000Z)
# ============================================================================
START_DATE = "2025-11-03T00:00:00.000Z"
END_DATE = "2025-11-09T23:59:59.000Z"
# ============================================================================


def parse_date_string(date_str: str) -> Optional[datetime.datetime]:
    """Parse ISO date string to datetime object."""
    if pd.isna(date_str) or not date_str:
        return None
    
    try:
        # Handle ISO format: "2025-09-10T08:49:46.000Z"
        if 'T' in str(date_str):
            return pd.to_datetime(date_str).replace(tzinfo=None)
        else:
            return pd.to_datetime(date_str)
    except:
        return None


def get_target_file(rim_dir: pathlib.Path) -> pathlib.Path:
    """Get the specific regulatory_objective__rim.csv file."""
    target_file = rim_dir / "regulatory_objective__rim.csv"
    if not target_file.exists():
        print(f"❌ ERROR: Target file not found: {target_file}")
        sys.exit(1)
    return target_file


def filter_rim_file(file_path: pathlib.Path, start_date: datetime.datetime,
                   end_date: datetime.datetime, output_file: pathlib.Path) -> Dict:
    """Filter a single RIM file based on modified_date__v column."""

    result = {
        'filename': file_path.name,
        'original_rows': 0,
        'filtered_rows': 0
    }

    print(f"Processing: {file_path.name}")

    # Read CSV file
    df = pd.read_csv(file_path, encoding='utf-8')
    result['original_rows'] = len(df)

    # Check if modified_date__v column exists
    if 'modified_date__v' not in df.columns:
        print(f"❌ ERROR: No 'modified_date__v' column in {file_path.name}")
        sys.exit(1)

    # Convert date column to datetime
    df['parsed_date'] = df['modified_date__v'].apply(parse_date_string)

    # Filter data within date range
    mask = (
        (df['parsed_date'] >= start_date) &
        (df['parsed_date'] <= end_date) &
        (df['parsed_date'].notna())
    )

    filtered_df = df[mask].drop('parsed_date', axis=1)
    result['filtered_rows'] = len(filtered_df)

    # Save filtered data
    filtered_df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"  SUCCESS: {result['original_rows']:,} -> {result['filtered_rows']:,} rows")

    return result


def create_summary_report(filter_result: Dict, start_date: str, end_date: str,
                         report_path: pathlib.Path):
    """Generate a summary report of the filtering process."""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RIM DATA MIGRATION FILTER REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Filter Date Range: {start_date} to {end_date}\n\n")

        # Summary statistics
        f.write("SUMMARY:\n")
        f.write("-" * 70 + "\n")
        f.write(f"File processed: {filter_result['filename']}\n")
        f.write(f"Original rows: {filter_result['original_rows']:,}\n")
        f.write(f"Filtered rows: {filter_result['filtered_rows']:,}\n")

        if filter_result['original_rows'] > 0:
            filter_percentage = (filter_result['filtered_rows'] / filter_result['original_rows']) * 100
            f.write(f"Filter retention rate: {filter_percentage:.2f}%\n")

        f.write("\n")

    print(f"  SUCCESS: Summary report saved: {report_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("RIM DATA MIGRATION FILTER SCRIPT")
    print("=" * 70)
    print(f"Filter Date Range: {START_DATE} to {END_DATE}")
    
    # Parse date range
    try:
        start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = datetime.datetime.strptime(END_DATE, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        print(f"❌ ERROR: Invalid date format")
        sys.exit(1)
    
    # Define paths
    rim_dir = pathlib.Path("03 Target RIM")
    output_file = pathlib.Path("02 - Filter RIM on migration data.csv")
    summary_report_file = pathlib.Path("02 - Filter RIM on migration data - Summary.txt")
    
    # Validate RIM directory
    if not rim_dir.exists():
        print(f"❌ RIM directory not found: {rim_dir}")
        sys.exit(1)
    
    print(f"Output files will be saved in root directory")

    # Get target file
    target_file = get_target_file(rim_dir)
    print(f"Target file: {target_file.name}")
    print()

    # Process the file
    result = filter_rim_file(target_file, start_date, end_date, output_file)

    # Generate summary report
    print("\nGenerating summary report...")
    create_summary_report(result, START_DATE, END_DATE, summary_report_file)

    # Final summary
    print("\n" + "=" * 70)
    print("FILTERING COMPLETED SUCCESSFULLY")
    print(f"File processed: {result['filename']}")
    print(f"Filtered rows: {result['filtered_rows']:,}")
    print(f"Output file: {output_file}")
    print(f"Summary report: {summary_report_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
