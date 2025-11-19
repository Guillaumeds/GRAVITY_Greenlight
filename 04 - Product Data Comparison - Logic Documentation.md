# Column Logic

**MVS_Unique_ID**: From MVS data

**Out_of_Scope**: From MVS scope column

**Count_in_MVS**: ID occurrences in MVS (grouped)

**Count_in_RO_Loader_Create**: ID occurrences in Create file external_id__v (pipe-split)

**Count_in_RO_Loader_Update**: ID occurrences in Update file external_id__c (pipe-split)

**Count_in_RIM**: ID occurrences in RIM external_id__c (pipe-split)

**Found_in_RIM**: "Yes" if Count_in_RIM > 0

**Green_Light_MVS**: From MVS green light column

**Greenlight_RO_Loader_Create**: From Create file greenlight_to_implement__c

**Greenlight_RO_Loader_Update**: From Update file agi_greenlight_to_implement__c

**Greenlight_RIM**: From RIM greenligh_to_implement__c

**MVS_Molecule**: From MVS molecule column

**RIM_Product_Name**: From RIM product name column

**Product_Match**: TRUE if all RIM molecules found in MVS molecules, FALSE if not, empty if RIM blank
