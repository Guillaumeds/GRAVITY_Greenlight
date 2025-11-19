# 02 - Filter RIM on Migration Data - Logic Documentation

## Business Logic

**GIVEN** RIM data file with modification dates exists  
**WHEN** script runs with date range filter  
**THEN** only records modified within migration date range are kept

## Core Process

### File Location
**GIVEN** "03 Target RIM" folder contains "regulatory_objective__rim_data.csv"  
**WHEN** script searches for target file  
**THEN** file is found and validated

### Date Range Setup
**GIVEN** START_DATE and END_DATE are configured in script  
**WHEN** dates are parsed  
**THEN** valid date range is established for filtering

### Data Filtering
**GIVEN** RIM file has "modified_date__v" column  
**WHEN** each row's date is checked  
**THEN** 
- ✅ **KEEP**: Date falls within range
- ❌ **REMOVE**: Date outside range or invalid

### Quality Validation
**GIVEN** original and filtered row counts  
**WHEN** filtering completes  
**THEN** retention rate is calculated and reported

## Verification Steps

1. **File Found**: Target CSV exists in RIM folder
2. **Date Column**: "modified_date__v" column present
3. **Filter Logic**: Only dates within range kept
4. **Output Created**: Filtered CSV and summary report generated

## Success Criteria
- Target file processed without errors
- Filtered data contains only records within date range
- Summary report shows retention rate
