# Script 02 Rewrite Summary - API Integration

## Changes Made

### Overview
Script `02 - Filter RIM on migration data.py` has been completely rewritten to pull fresh data directly from Veeva RIM PROD via API instead of filtering a local CSV file.

### Key Changes

#### Before (Old Version)
- **Data Source**: Local CSV file from `03 Target RIM/regulatory_objective__rim.csv`
- **Operation**: Date-range filtering on `modified_date__v` column
- **Method**: Pandas CSV reading and filtering
- **Configuration**: Manual START_DATE and END_DATE settings

#### After (New Version)
- **Data Source**: Veeva RIM PROD API (Live)
- **Operation**: Complete extract with no filtering
- **Method**: REST API with VQL (Vault Query Language)
- **Configuration**: Credentials from `.env` file

### Technical Implementation

#### API Integration
1. **Authentication**: Username/password authentication to get session token
2. **Query**: VQL query to select all fields from `regulatory_objective__rim`
3. **Pagination**: Automatic handling of large datasets (1000 records per page)
4. **Rate Limiting**: 0.1 second delay between requests to respect API limits

#### Fields Retrieved
The script now extracts the following fields:
- `id`, `name__v`, `status__v`, `lifecycle__v`
- `created_date__v`, `created_by__v`
- `modified_date__v`, `modified_by__v`
- `date_of_greenlight__c`, `additional_implementation_info__c`

#### Dependencies
- `requests` - HTTP library for API calls ✓ Already installed
- `python-dotenv` - Environment variable management ✓ Already installed
- `pandas` - Data manipulation (already used)

### Configuration

The script reads credentials from `.env` file:
```
VEEVA_PROD_USERNAME=agi.api@aspenpharma.com
VEEVA_PROD_PASSWORD=gmv@xqf0fdq*kzr2CDX
VEEVA_PROD_BASE_URL=https://aspenpharma-rim.veevavault.com/api/v25.2
VEEVA_RATE_LIMIT_DELAY=0.1
```

### Benefits

1. **Always Fresh**: Gets latest data directly from PROD on every run
2. **No Manual Exports**: Eliminates need to manually export RIM data
3. **Complete Data**: No date filtering - gets all records
4. **Automated**: Can be scheduled to run automatically
5. **Audit Trail**: API logs all data access

### How to Use

1. Ensure `.env` file exists with valid PROD credentials
2. Run script: `py "02 - Filter RIM on migration data.py"`
3. Script will:
   - Authenticate with Veeva Vault
   - Query all regulatory_objective__rim records
   - Handle pagination automatically
   - Save complete extract to CSV
   - Generate summary report

### Output Files

Same as before:
- `02 - Filter RIM on migration data.csv` - Complete data extract
- `02 - Filter RIM on migration data - Summary.txt` - Extraction report

### API Documentation Reference

Based on Veeva Vault API v24.3/v25.2:
- **Authentication**: `POST /api/{version}/auth`
- **Query**: `POST /api/{version}/query` with VQL
- **Pagination**: Uses `LIMIT` and `OFFSET` parameters
- **Max Page Size**: 1000 records per request
- **Response Format**: JSON

### Important Notes

1. **No Filtering**: This version extracts ALL records, no date filtering applied
2. **API Permissions**: User must have API access and read permissions for regulatory_objective__rim object
3. **Rate Limits**: Script respects Veeva API rate limits with 0.1s delays
4. **Network Required**: Requires internet connection to reach Veeva Vault PROD
5. **Credentials Security**: Ensure .env file is not committed to version control

### Next Steps

If date filtering is needed:
1. Keep this script for fresh extracts
2. Create a separate filtering script that processes the CSV output
3. Or add WHERE clause to VQL query (e.g., `WHERE modified_date__v >= '2025-11-01'`)

### Documentation Updates

- Updated `02 - Filter RIM - Logic Documentation.md` to reflect API approach
- Removed date filtering logic documentation
- Added API authentication and pagination details

## Testing Recommendations

Before production use:
1. Test authentication with PROD credentials
2. Verify all expected fields are returned
3. Check pagination works correctly (if > 1000 records)
4. Validate output CSV format matches expectations
5. Confirm downstream scripts can read the new output

---
**Date Updated**: 2025-11-19  
**Script Version**: 2.0 (API Integration)  
**API Version**: Veeva Vault v25.2
