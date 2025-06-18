import pandas as pd

# to open virtual environment: venv\Scripts\activate

# === STEP 1: load CSVs ===
df = pd.read_csv('211 Call Data_Client Tab_All Years.csv')
df_public = pd.read_csv('211 Area Indicators_ZipZCTA.csv')

# === STEP 2: preview columns ===
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

# === STEP 3: clean ZIP code column ===
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

# === STEP 4: count calls per ZIP ===
zip_counts = df_clean['ClientAddressus_ClientAddressus_zip'].value_counts().reset_index()
zip_counts.columns = ['zip_code', 'total_callers']

# clean ZIP codes to match format
zip_counts['zip_code'] = zip_counts['zip_code'].astype(str).str.extract(r'(\d{5})')

# === STEP 5: pull ZIP + pop ===
df_public['zip_code'] = df_public['GEO.display_label'].astype(str).str.extract(r'(\d{5})')
zip_pop = df_public[['zip_code', 'Pop_Estimate']]
zip_pop.columns = ['zip_code', 'population']

# === STEP 6: merge + calc calls per 1000 ===
zip_data = pd.merge(zip_counts, zip_pop, on='zip_code', how='left')
zip_data['population'] = zip_data['population'].fillna(1)
zip_data['callers_per_1000'] = (zip_data['total_callers'] / zip_data['population']) * 1000
zip_data = zip_data.dropna(subset=['zip_code'])
zip_data = zip_data[zip_data['population'] > 500]  # or try 750 for smoother scaling

# === STEP 7: save final results ===
zip_data.to_csv('Callers_Per_1000.csv', index=False)
zip_counts.to_csv('Callers_By_Zip.csv', index=False)

print("\nTop 10 ZIP codes by call count:")
print(zip_counts.head(10))
print(zip_data.head(10))


'''
THIS IS CODE VISUALIZATION!!!
'''


import matplotlib.pyplot as plt
# remove extreme outlier ZIP 78205 for visual clarity
zip_data = zip_data[zip_data['zip_code'] != '78205']

# sort by callers per 1,000
zip_data_sorted = zip_data.sort_values(by='callers_per_1000', ascending=False)

'''
ZIP code 78205 (Downtown San Antonio) had an exceptionally high callers-per-1,000 rate (~2,972) due to a small residential population and the presence of shelters or public services.
It was removed from the graph for visualization clarity but noted here due to its importance.
'''

plt.figure(figsize=(20,6))
plt.bar(zip_data_sorted['zip_code'], zip_data_sorted['callers_per_1000'], color="#ffbed9")  # light pink

plt.title('2-1-1 Callers Per 1,000 Residents by ZIP Code')
plt.xlabel('ZIP Code (sorted by highest rate)')
plt.ylabel('Callers Per 1,000 Residents')
plt.xticks(rotation=90, ha='center', fontsize=9)  # smaller font for spacing
plt.tight_layout()
plt.show()

'''
Okay so now were gonna do calls per zip
'''
# sort ALL ZIPs by total callers (raw count)
zip_counts_sorted = zip_counts.sort_values(by='total_callers', ascending=False)

# clean ZIP codes: convert to string and pad with zeros
zip_counts_sorted['zip_code'] = zip_counts_sorted['zip_code'].astype(str).str.zfill(5)

plt.figure(figsize=(20,6))
plt.bar(zip_counts_sorted['zip_code'], zip_counts_sorted['total_callers'], color='#ffbed9')  # light pink

plt.title('2-1-1 Total Callers by ZIP Code')
plt.xlabel('ZIP Code (sorted by total callers)')
plt.ylabel('Total Callers')
plt.xticks(rotation=90, ha='center', fontsize=9)
plt.tight_layout()
plt.show()