#!/usr/bin/env python3
"""
Migration Configuration File
Centralized configuration for migration date ranges and other settings.
All scripts should import and use these settings for consistency.
"""

# Migration Date Range Configuration
# Format: YYYY-MM-DDTHH:MM:SS.000Z (RIM ISO format)
# Example: 2025-09-12T16:38:00.000Z

MIGRATION_START_DATE = "2025-09-10T00:00:00.000Z"
MIGRATION_END_DATE = "2025-09-18T23:59:59.000Z"

# Date column names in RIM data
RIM_CREATED_DATE_COLUMN = "created_date__v"
RIM_MODIFIED_DATE_COLUMN = "modified_date__v"

# File paths (relative to script directory)
RIM_FILTERED_FILE = "02 - Filter RIM on migration data.csv"
LOADER_CREATE_FILE = "02 Loader sheets/regulatory_objective__rim.csv"
LOADER_UPDATE_FILE = "02 Loader sheets/regulatory_objective_rim_update.csv"

def get_migration_date_range():
    """Get migration date range as tuple."""
    return MIGRATION_START_DATE, MIGRATION_END_DATE

def get_rim_date_columns():
    """Get RIM date column names as tuple."""
    return RIM_CREATED_DATE_COLUMN, RIM_MODIFIED_DATE_COLUMN
