# 02 - Extract Fresh RIM Data from PROD - Logic Documentation

## Business Logic

**GIVEN** Veeva RIM PROD API credentials are configured  
**WHEN** script runs  
**THEN** fresh complete extract of regulatory_objective__rim is retrieved via API

## Core Process

### API Authentication
**GIVEN** .env file contains PROD credentials  
**WHEN** script authenticates with Veeva Vault  
**THEN** valid session token is obtained

### Data Extraction
**GIVEN** authenticated API session  
**WHEN** VQL query executes against regulatory_objective__rim object  
**THEN** 
- All records are retrieved from PROD
- Pagination handled automatically (1000 records per page)
- No filtering applied - complete extract

### Data Fields Retrieved
The following fields are extracted from regulatory_objective__rim:
- `id` - Record ID
- `name__v` - Record name
- `status__v` - Record status
- `lifecycle__v` - Lifecycle state
- `created_date__v` - Creation timestamp
- `created_by__v` - Creator user ID
- `modified_date__v` - Last modification timestamp
- `modified_by__v` - Last modifier user ID
- `date_of_greenlight__c` - Greenlight date
- `additional_implementation_info__c` - Implementation info

### Pagination Handling
**GIVEN** large dataset in RIM PROD  
**WHEN** query returns more than 1000 records  
**THEN** 
- Script automatically fetches additional pages
- Uses OFFSET and LIMIT parameters
- Respects API rate limits (0.1s delay between requests)

### Output Generation
**GIVEN** records retrieved successfully  
**WHEN** data is saved  
**THEN** 
- CSV file created with all records
- Summary report generated with extraction details
- Execution time tracked

## Verification Steps

1. **Environment**: .env file contains valid PROD credentials
2. **Authentication**: Successfully connects to Veeva Vault API
3. **Query Execution**: VQL query returns records
4. **Pagination**: All pages retrieved if dataset > 1000 records
5. **Output Created**: CSV and summary report generated

## Success Criteria
- Successful API authentication
- Complete dataset extracted (all pages)
- No records filtered out
- CSV contains all available RIM PROD records
- Summary report shows record count and columns

## Data Source
- **Source**: Veeva RIM PROD (Live API)
- **Method**: REST API with VQL queries
- **Version**: API v25.2
- **Object**: `regulatory_objective__rim`
- **No Filtering**: Complete extract, no date range filtering
