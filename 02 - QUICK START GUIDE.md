# Quick Start Guide - Script 02 (API Version)

## What Changed?
Script 02 now pulls data directly from Veeva RIM PROD via API instead of reading a local CSV file.

## Prerequisites
✓ `.env` file exists with PROD credentials  
✓ Internet connection to reach Veeva Vault  
✓ Python packages: `requests`, `python-dotenv`, `pandas` (all installed)

## How to Run

### Option 1: PowerShell
```powershell
py "02 - Filter RIM on migration data.py"
```

### Option 2: Command Prompt
```cmd
python "02 - Filter RIM on migration data.py"
```

## What It Does

1. **Authenticates** with Veeva Vault PROD using credentials from .env
2. **Queries** all records from `regulatory_objective__rim` object
3. **Handles pagination** automatically (fetches all pages)
4. **Saves** complete extract to CSV file
5. **Generates** summary report

## Expected Output

### Console Output
```
======================================================================
RIM PROD DATA EXTRACTION SCRIPT
======================================================================
Extracting fresh data from regulatory_objective__rim object
Source: Veeva RIM PROD via API

Authenticating with Veeva Vault...
URL: https://aspenpharma-rim.veevavault.com/api/v25.2
User: agi.api@aspenpharma.com
✓ Authentication successful

Executing VQL query...
Query: SELECT id, name__v, status__v...
  Page: offset=0, size=1000, total=2500
  Page: offset=1000, size=1000, total=2500
  Page: offset=2000, size=500, total=2500
✓ Query complete: Retrieved 2500 records

Saving 2500 records to CSV...
✓ Saved to: 02 - Filter RIM on migration data.csv
  Rows: 2,500
  Columns: 10

Generating summary report...
✓ Summary report saved: 02 - Filter RIM on migration data - Summary.txt

======================================================================
EXTRACTION COMPLETED SUCCESSFULLY
Records extracted: 2,500
Execution time: 15.43 seconds
Output file: 02 - Filter RIM on migration data.csv
Summary report: 02 - Filter RIM on migration data - Summary.txt
======================================================================
```

### Files Created
- `02 - Filter RIM on migration data.csv` - Complete data extract
- `02 - Filter RIM on migration data - Summary.txt` - Extraction summary

## Fields Extracted

The following fields are retrieved from RIM PROD:
- `id` - Record ID
- `name__v` - Record name
- `status__v` - Record status
- `lifecycle__v` - Lifecycle state
- `created_date__v` - Creation timestamp
- `created_by__v` - Creator user ID
- `modified_date__v` - Last modification timestamp
- `modified_by__v` - Last modifier user ID
- `date_of_greenlight__c` - Greenlight date (custom field)
- `additional_implementation_info__c` - Implementation info (custom field)

## Troubleshooting

### Error: "Missing required environment variables"
**Solution**: Check that .env file exists and contains:
```
VEEVA_PROD_USERNAME=...
VEEVA_PROD_PASSWORD=...
VEEVA_PROD_BASE_URL=...
```

### Error: "Authentication failed"
**Solution**: 
- Verify credentials in .env are correct
- Check if API user account is active
- Confirm user has API access permissions

### Error: "Query failed"
**Solution**:
- Verify object name `regulatory_objective__rim` is correct
- Check user has read permissions for this object
- Review field names in VQL query match RIM schema

### No records returned
**Solution**:
- Object might be empty in PROD
- User might not have permissions
- Check VQL query syntax

### Connection timeout
**Solution**:
- Verify internet connection
- Check Veeva Vault URL is correct
- Try again (network issues)

## API Rate Limits

- Script automatically waits 0.1 seconds between pagination requests
- Veeva Vault has authentication rate limits (check with admin if errors occur)
- Large extracts may take several minutes

## Security Notes

⚠️ **Important**: 
- Never commit .env file to Git
- Keep API credentials secure
- API user should have read-only permissions
- All API calls are logged by Veeva

## Customization

### Change Fields Retrieved
Edit the `VQL_QUERY` variable in the script:
```python
VQL_QUERY = """
SELECT 
    id,
    name__v,
    your_custom_field__c
FROM regulatory_objective__rim
""".strip()
```

### Add Date Filtering
Add WHERE clause to VQL query:
```python
VQL_QUERY = """
SELECT id, name__v
FROM regulatory_objective__rim
WHERE modified_date__v >= '2025-11-01'
""".strip()
```

### Change Rate Limit Delay
Update in .env file:
```
VEEVA_RATE_LIMIT_DELAY=0.2
```

## Next Steps

After successful extraction:
1. Review output CSV to verify data
2. Check summary report for record counts
3. Run downstream scripts (03, 04, etc.) with fresh data
4. Monitor execution time for large datasets

---
**Version**: 2.0 (API Integration)  
**Last Updated**: 2025-11-19
