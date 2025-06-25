import pandas as pd

# to open virtual environment: venv\Scripts\activate

'''
This Python file performs foundational ZIP-level cleaning and summary for 2-1-1 client data. 
Its primary goal is to generate cleaned ZIP code data for overall call volume analysis and 
visualization, particularly for exploratory and operations-focused use cases.

Key actions:
- Removes full-row duplicates and deduplicates by Client_Id (to count unique callers)
- Standardizes ZIP code format and handles missing/invalid entries
- Joins ZIP-level census data (population estimates) to compute normalized call rates
- Outputs ZIP-level summaries and visualizations (e.g., total callers, callers per 1,000 residents)

Unlike the more rigorous cleanup done in the 'Filter Callers ZIP Calls.py' file:
- This script **does not** remove postal ZIPs or cross-check ZIPs against the census ZIP list
- It **does not** remove "Phantom" or "Wrong #" calls
- It preserves more raw entries to capture a fuller picture of total caller presence,
  which is important for internal operational insight and volume-based evaluations

This file complements the stricter cleanup file, offering a more inclusive snapshot 
of ZIP-based call patterns across the region.
'''


# load CSVs
df = pd.read_csv('211 Call Data_Client Tab_All Years.csv')
df_public = pd.read_csv('211 Area Indicators_ZipZCTA.csv')

# preview columns
print("Column names:", df.columns.tolist())
print(df.head())

# check original shape
print(f"Original shape: {df.shape}")

# remove full-row duplicates
duplicates = df[df.duplicated()]
print(f"Number of duplicate rows: {duplicates.shape[0]}")

# drop duplicates by client ID
print("Before:", df.shape)
df_clean = df.drop_duplicates(subset=['Client_Id'])
print("After:", df_clean.shape)

# save cleaned version
df_clean.to_csv('211_Client_Cleaned.csv', index=False)

# clean ZIP code column
df_clean['ClientAddressus_ClientAddressus_zip'] = (
    df_clean['ClientAddressus_ClientAddressus_zip']
    .fillna('Unknown')
    .replace('', 'Unknown')
    .astype(str)
    .str.strip()
    .replace(['', 'nan', '0.0', '0'], 'Unknown')
)

# save again just in case
df_clean.to_csv('211_Client_Cleaned.csv', index=False)

# check how many unknown ZIPs
unknown_count = df_clean[df_clean['ClientAddressus_ClientAddressus_zip'] == 'Unknown'].shape[0]
print(f"Number of 'Unknown' ZIP codes: {unknown_count}")

# count calls per ZIP
zip_counts = df_clean['ClientAddressus_ClientAddressus_zip'].value_counts().reset_index()
zip_counts.columns = ['zip_code', 'total_callers']

# clean ZIP codes to match format
zip_counts['zip_code'] = zip_counts['zip_code'].astype(str).str.extract(r'(\d{5})')

# pull ZIP + pop
df_public['zip_code'] = df_public['GEO.display_label'].astype(str).str.extract(r'(\d{5})')
zip_pop = df_public[['zip_code', 'Pop_Estimate']]
zip_pop.columns = ['zip_code', 'population']

# merge + calc calls per 1000
zip_data = pd.merge(zip_counts, zip_pop, on='zip_code', how='left')
zip_data['population'] = zip_data['population'].fillna(1)
zip_data['callers_per_1000'] = (zip_data['total_callers'] / zip_data['population']) * 1000
zip_data = zip_data.dropna(subset=['zip_code'])
zip_data = zip_data[zip_data['population'] > 500]  # or try 750 for smoother scaling

# save final results
zip_data.to_csv('Callers_Per_1000.csv', index=False)
zip_counts.to_csv('Callers_By_Zip.csv', index=False)

print("\nTop 10 ZIP codes by call count:")
print(zip_counts.head(10))
print(zip_data.head(10))


'''
THIS IS CODE VISUALIZATION!!!
'''

import matplotlib.pyplot as plt

'''
2-1-1 Callers per 1,000 vs. Population by ZIP Code Scatter Plot
'''

plt.figure(figsize=(10, 6))

# scatter plot
plt.scatter(zip_data['population'], zip_data['callers_per_1000'], color="#253791", alpha=0.7)  # United Way Blue

# highlight outlier
highlight = zip_data[zip_data['zip_code'] == '78205']
plt.scatter(highlight['population'], highlight['callers_per_1000'], color="#EF3A43", label='Outliers')  # Red

# label 78205 manually near the top of y-axis
for _, row in highlight.iterrows():
    plt.text(row['population'], 950, '78205', fontsize=8, ha='center', color="#EF3A43")
    plt.annotate('Outlier (Call Rate ~2972)', 
                 xy=(row['population'], 950), 
                 xytext=(row['population']+5000, 970), 
                 arrowprops=dict(arrowstyle="->", color="#A0A0A0"),
                 fontsize=8, color="#A0A0A0")

# label top 10 ZIPs (excluding 78205)
top_zips = zip_data[zip_data['zip_code'] != '78205'] \
    .sort_values(by='callers_per_1000', ascending=False) \
    .head(10)

for _, row in top_zips.iterrows():
    plt.text(row['population'], row['callers_per_1000'] + 10, row['zip_code'],
             fontsize=8, ha='center', color="#1A237E")

# chart styling
plt.title('Callers per 1,000 vs. Population by ZIP Code', color="#253791")
plt.xlabel('ZIP Code Population', color="#253791")
plt.ylabel('Callers per 1,000 Residents', color="#253791")
plt.ylim(0, 1000)
plt.legend()
plt.grid(True, color="#E6E6E6", linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


'''
2-1-1 Total Callers by ZIP Code Line Graph
'''

# make a copy to preserve original
zip_counts_sorted = zip_counts.copy()

# ensure ZIP codes are strings and properly formatted
zip_counts_sorted['zip_code'] = zip_counts_sorted['zip_code'].astype(str).str.zfill(5)

# filter out invalid or missing ZIPs and zero-call entries
zip_counts_sorted = zip_counts_sorted[
    (zip_counts_sorted['zip_code'] != 'Unknown') &
    (zip_counts_sorted['zip_code'].str.match(r'^\d{5}$')) &
    (zip_counts_sorted['total_callers'] > 0)
].sort_values(by='total_callers', ascending=False).reset_index(drop=True)

#prepare call data
# remove outlier ZIP 78205
zip_data_sorted = zip_data[zip_data['zip_code'] != '78205'].copy()

# plot the total callers by ZIP

fig, ax = plt.subplots(figsize=(30, 8), constrained_layout=True)

ax.plot(zip_counts_sorted['zip_code'], zip_counts_sorted['total_callers'],
        color="#253791", marker='o', markersize=2, linewidth=1)

ax.set_xticks(range(len(zip_counts_sorted)))
ax.set_xticklabels(zip_counts_sorted['zip_code'], rotation=60, ha='right', fontsize=6)

ax.set_xlabel('ZIP Code (sorted by total callers)', fontsize=10, color="#253791")
ax.set_ylabel('Total Callers', fontsize=10, labelpad=15, color="#253791")
ax.set_title('2-1-1 Total Callers by ZIP Code', fontsize=12, color="#253791")
ax.grid(axis='y', linestyle='--', alpha=0.5, color="#E6E6E6")

plt.show()

'''
2-1-1 Callers per 1,000 Residents Line Graph
'''
zip_data_sorted = zip_data_sorted.sort_values(by='callers_per_1000', ascending=False)

fig, ax = plt.subplots(figsize=(30, 8), constrained_layout=True)

ax.plot(zip_data_sorted['zip_code'], zip_data_sorted['callers_per_1000'],
        color="#253791", marker='o', markersize=2, linewidth=1)

ax.set_xticks(range(len(zip_data_sorted)))
ax.set_xticklabels(zip_data_sorted['zip_code'], rotation=60, ha='right', fontsize=6)

ax.set_xlabel('ZIP Code (sorted by callers per 1,000 residents)', fontsize=10, color="#253791")
ax.set_ylabel('Callers per 1,000 Residents', fontsize=10, labelpad=15, color="#253791")
ax.set_title('2-1-1 Callers per 1,000 Residents by ZIP Code', fontsize=12, color="#253791")
ax.grid(axis='y', linestyle='--', alpha=0.5, color="#E6E6E6")

plt.show()