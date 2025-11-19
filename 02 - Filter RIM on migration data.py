#!/usr/bin/env python3
"""
02 - Extract Fresh RIM Data from PROD
Connects to Veeva RIM PROD via API and extracts all regulatory_objective__rim records.
No filtering applied - pulls fresh complete extract.
"""

import os
import sys
import time
import json
import pathlib
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from urllib.parse import urljoin


# ============================================================================
# CONFIGURATION
# ============================================================================
# Load environment variables from .env file
load_dotenv()

VEEVA_USERNAME = os.getenv("VEEVA_PROD_USERNAME")
VEEVA_PASSWORD = os.getenv("VEEVA_PROD_PASSWORD")
VEEVA_BASE_URL = os.getenv("VEEVA_PROD_BASE_URL")
VEEVA_RATE_LIMIT_DELAY = float(os.getenv("VEEVA_RATE_LIMIT_DELAY", "0.1"))

# Veeva API endpoints
AUTH_ENDPOINT = "/auth"
QUERY_ENDPOINT = "/query"

# Output configuration
OUTPUT_FILE = pathlib.Path("02 - Filter RIM on migration data.csv")
SUMMARY_REPORT_FILE = pathlib.Path("02 - Filter RIM on migration data - Summary.txt")

# VQL query for regulatory_objective__rim object
# Note: Adjust fields as needed based on your RIM object schema
VQL_QUERY = """
SELECT 
    id, 
    name__v, 
    status__v,
    lifecycle__v,
    created_date__v,
    created_by__v,
    modified_date__v,
    modified_by__v,
    date_of_greenlight__c,
    additional_implementation_info__c
FROM regulatory_objective__rim
""".strip()


# ============================================================================
# VEEVA VAULT API FUNCTIONS
# ============================================================================

class VeevaVaultAPI:
    """Veeva Vault API client with authentication and querying capabilities."""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session_id = None
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """Authenticate with Veeva Vault and obtain session ID."""
        print(f"Authenticating with Veeva Vault...")
        print(f"URL: {self.base_url}")
        print(f"User: {self.username}")
        
        auth_url = self.base_url + AUTH_ENDPOINT
        
        try:
            response = self.session.post(
                auth_url,
                data={
                    'username': self.username,
                    'password': self.password
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('responseStatus') == 'SUCCESS':
                    self.session_id = result.get('sessionId')
                    print(f"✓ Authentication successful")
                    return True
                else:
                    print(f"❌ Authentication failed: {result.get('responseMessage', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def execute_vql_query(self, query: str) -> List[Dict]:
        """
        Execute VQL query and return all records, handling pagination automatically.
        
        Args:
            query: VQL query string
            
        Returns:
            List of record dictionaries
        """
        if not self.session_id:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        all_records = []
        page_offset = 0
        page_size = 1000  # Maximum page size for VQL queries
        
        print(f"\nExecuting VQL query...")
        print(f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
        
        while True:
            query_url = self.base_url + QUERY_ENDPOINT
            
            headers = {
                'Authorization': self.session_id,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            # Add pagination parameters
            paginated_query = query
            if page_offset > 0:
                paginated_query = f"{query} LIMIT {page_size} OFFSET {page_offset}"
            else:
                paginated_query = f"{query} LIMIT {page_size}"
            
            try:
                response = self.session.post(
                    query_url,
                    data={'q': paginated_query},
                    headers=headers
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP Error {response.status_code}: {response.text}")
                
                result = response.json()
                
                if result.get('responseStatus') != 'SUCCESS':
                    error_msg = result.get('errors', [{}])[0].get('message', 'Unknown error')
                    raise Exception(f"Query failed: {error_msg}")
                
                # Extract records
                response_details = result.get('responseDetails', {})
                data = result.get('data', [])
                
                total_records = response_details.get('total', 0)
                current_size = response_details.get('size', 0)
                page_offset_current = response_details.get('pageoffset', 0)
                
                print(f"  Page: offset={page_offset_current}, size={current_size}, total={total_records}")
                
                all_records.extend(data)
                
                # Check if we have more records to fetch
                if len(all_records) >= total_records or current_size == 0:
                    break
                
                # Move to next page
                page_offset += page_size
                
                # Rate limiting - respect Veeva API limits
                time.sleep(VEEVA_RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"❌ Query error: {str(e)}")
                raise
        
        print(f"✓ Query complete: Retrieved {len(all_records)} records")
        return all_records
    
    def close(self):
        """Close the session."""
        self.session.close()


# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

def validate_environment_variables():
    """Validate that all required environment variables are set."""
    required_vars = {
        'VEEVA_PROD_USERNAME': VEEVA_USERNAME,
        'VEEVA_PROD_PASSWORD': VEEVA_PASSWORD,
        'VEEVA_PROD_BASE_URL': VEEVA_BASE_URL
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease check your .env file.")
        return False
    
    return True


def save_records_to_csv(records: List[Dict], output_file: pathlib.Path) -> int:
    """
    Save records to CSV file.
    
    Args:
        records: List of record dictionaries
        output_file: Path to output CSV file
        
    Returns:
        Number of records saved
    """
    if not records:
        print("⚠ Warning: No records to save")
        return 0
    
    print(f"\nSaving {len(records)} records to CSV...")
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Save to CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✓ Saved to: {output_file}")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    
    return len(df)


def create_summary_report(record_count: int, columns: List[str], 
                         report_path: pathlib.Path, execution_time: float):
    """Generate a summary report of the extraction process."""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RIM PROD DATA EXTRACTION REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: Veeva RIM PROD API\n")
        f.write(f"Object: regulatory_objective__rim\n")
        f.write(f"Execution time: {execution_time:.2f} seconds\n\n")
        
        f.write("SUMMARY:\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total records extracted: {record_count:,}\n")
        f.write(f"Total columns: {len(columns)}\n\n")
        
        f.write("COLUMNS EXTRACTED:\n")
        f.write("-" * 70 + "\n")
        for i, col in enumerate(columns, 1):
            f.write(f"{i:3d}. {col}\n")
        
        f.write("\n")
        f.write("NOTE: This is a complete fresh extract from RIM PROD.\n")
        f.write("No filtering has been applied.\n")
    
    print(f"✓ Summary report saved: {report_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    start_time = time.time()
    
    print("=" * 70)
    print("RIM PROD DATA EXTRACTION SCRIPT")
    print("=" * 70)
    print(f"Extracting fresh data from regulatory_objective__rim object")
    print(f"Source: Veeva RIM PROD via API")
    print()
    
    # Validate environment variables
    if not validate_environment_variables():
        sys.exit(1)
    
    # Initialize API client
    api = VeevaVaultAPI(VEEVA_BASE_URL, VEEVA_USERNAME, VEEVA_PASSWORD)
    
    try:
        # Authenticate
        if not api.authenticate():
            print("\n❌ Failed to authenticate with Veeva Vault")
            sys.exit(1)
        
        print()
        
        # Execute VQL query to get all records
        records = api.execute_vql_query(VQL_QUERY)
        
        if not records:
            print("\n⚠ Warning: No records returned from query")
            print("This could mean:")
            print("  - The object is empty")
            print("  - The VQL query syntax is incorrect")
            print("  - You don't have permissions to read this object")
            sys.exit(1)
        
        # Save to CSV
        record_count = save_records_to_csv(records, OUTPUT_FILE)
        
        # Get column names from first record
        columns = list(records[0].keys()) if records else []
        
        # Generate summary report
        execution_time = time.time() - start_time
        print("\nGenerating summary report...")
        create_summary_report(record_count, columns, SUMMARY_REPORT_FILE, execution_time)
        
        # Final summary
        print("\n" + "=" * 70)
        print("EXTRACTION COMPLETED SUCCESSFULLY")
        print(f"Records extracted: {record_count:,}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Output file: {OUTPUT_FILE}")
        print(f"Summary report: {SUMMARY_REPORT_FILE}")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        api.close()


if __name__ == "__main__":
    main()
