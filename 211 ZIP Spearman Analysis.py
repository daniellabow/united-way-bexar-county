import pandas as pd
from scipy.stats import spearmanr

# load data from CSV files created in 'Client ZIP Code Cleanup' and 'Poverty Cleanup'
zip_data = pd.read_csv('Callers_Per_1000.csv')    # CRITERIA: should include 'zip_code', 'total_callers', 'callers_per_1000'
df_econ = pd.read_csv('Top_ZIPs_Economic_Instabiloty.csv')    # CRITERIA: should include 'zip_code', 'poverty_rate', 'alice_rate', 'econ_instability'

# now merge on ZIP code
merged = pd.merge(zip_data, df_econ, on='zip_code')
print(f"Merged DataFrame: {merged.shape[0]} rows")

# now spearman correlation test code beginsss
