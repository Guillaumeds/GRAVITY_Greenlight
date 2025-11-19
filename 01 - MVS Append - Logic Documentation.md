# 01 - MVS Append Script - Logic Documentation

## Business Logic

**GIVEN** multiple Excel files exist in "01 Source MVS" folder
**WHEN** the script runs
**THEN** all files are combined into one CSV file with data integrity validation

## Core Process

### File Discovery
**GIVEN** source folder contains Excel files (.xlsx, .xls)
**WHEN** script searches for files
**THEN** all Excel files are found and counted

### Data Reading
**GIVEN** each Excel file has data
**WHEN** file is opened
**THEN** first row is skipped, all other data is read

### Data Combination
**GIVEN** all files are successfully read
**WHEN** data is combined
**THEN** all rows from all files are stacked together (no data loss)

### Quality Validation
**GIVEN** individual file row counts and combined file row count
**WHEN** validation runs
**THEN**
- ✅ **PASS**: Individual rows = Combined rows (perfect)
- ⚠️ **WARN**: Combined > Individual (duplication)
- ❌ **FAIL**: Combined < Individual (data loss)

## Verification Steps

1. **File Count**: Manual count = Script count
2. **Processing**: No error messages during reading
3. **Validation**: Quality report shows "PASSED"
4. **Output**: CSV file created successfully

## Success Criteria
- All files processed without errors
- Row count validation = PASSED
- Output files created (CSV + Quality report)
