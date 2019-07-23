# Accounting
Code for accounting and finance functions

Depreciation file: coding for automating depreciation outside normal variables and taking into account:

1. Different thresholds for different countries
2. Financial years that do not follow Gregorian Calendar 
3. Different useful lives of different countries
4. Differences in GAAPs between countries 

Calculates depreciation for the current financial year, initial and final balances (book values), months until the asset is fully depreciated and if this financial year is the last financial year for this asset. Also gets rid of assets with an initial balance of zero (fully depreciated before the start of the current FY) 
