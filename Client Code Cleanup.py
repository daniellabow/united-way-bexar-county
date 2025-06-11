import pandas as pd


# to open virtual environment: venv\Scripts\activate


# === STEP 1: load CSV ===
df = pd.read_csv('211 Call Data_Client Tab_All Years.csv')
df_public = pd.read_csv('uszips.csv')

# === STEP 2: preview the columns ===
print("Column names:", df.columns.tolist())
print(df.head())


# check how many rows and columns
print(f"Original shape: {df.shape}")


# this line removes any rows in the df that are completely identical across all columns
duplicates = df[df.duplicated()]
print(f"Number of duplicate rows: {duplicates.shape[0]}")


# now, removing duplicates of client id
# confirming the change went through
print("Before:", df.shape)
df_clean = df.drop_duplicates(subset=['Client_Id'])
print("After:", df_clean.shape)
# confirming change to file
df_clean.to_csv('211_Client_Cleaned.csv', index=False)

# check for missing data in zip code column
print(df['ClientAddressus_ClientAddressus_zip'].isnull().sum())

# filling in the blanks lol
df_clean.loc[:, 'ClientAddressus_ClientAddressus_zip'] = df_clean['ClientAddressus_ClientAddressus_zip'].fillna('Unknown')
df_clean.loc[:, 'ClientAddressus_ClientAddressus_zip'] = df_clean['ClientAddressus_ClientAddressus_zip'].replace('', 'Unknown')
df_clean.loc[:, 'ClientAddressus_ClientAddressus_zip'] = df_clean['ClientAddressus_ClientAddressus_zip'].astype(str).str.strip()
df_clean.loc[:, 'ClientAddressus_ClientAddressus_zip'] = df_clean['ClientAddressus_ClientAddressus_zip'].replace(['', 'nan', '0.0', '0'], 'Unknown')

# updating csv
df_clean.to_csv('211_Client_Cleaned.csv', index=False)

# just checking how many unkowns there are if any
unknown_count = df_clean[df_clean['ClientAddressus_ClientAddressus_zip'] == 'Unknown'].shape[0]
print(f"Number of 'Unknown' ZIP codes: {unknown_count}")

# count calls per ZIP code
zip_counts = df_clean['ClientAddressus_ClientAddressus_zip'].value_counts().reset_index()

# rename the columns for clarity
zip_counts.columns = ['zip_code', 'total_calls']

# make zip codes strings in both dataframes
zip_counts['zip_code'] = zip_counts['zip_code'].astype(str).str.zfill(5)
df_public['zip'] = df_public['zip'].astype(str).str.zfill(5)

# extract just ZIP and population
zip_pop = df_public[['zip', 'population']]
zip_pop.columns = ['zip_code', 'population']

# merge call counts with population data
zip_data = pd.merge(zip_counts, zip_pop, on='zip_code', how='left')

# fill missing population data with 1 to avoid division by zero
zip_data['population'] = zip_data['population'].fillna(1)

# Calculate calls per 1,000 residents
zip_data['calls_per_1000'] = (zip_data['total_calls'] / zip_data['population']) * 1000

# Save final results
zip_data.to_csv('Calls_Per_1000.csv', index=False)
print(zip_data.head(10))

# preview the result
print("\nTop 10 ZIP codes by call count")
print(zip_counts.head(10))

zip_counts.to_csv('Calls_By_Zip.csv', index=False)

#calls_per_1000 = (total_calls / population) * 1000


'''
CODE FOR VISUALIZATION PUPOSES!!!
'''
import matplotlib.pyplot as plt
import seaborn as sns

# sort data for plotting
zip_data_sorted = zip_data.sort_values(by='zip_code')

# plot
plt.figure(figsize=(14,6))
sns.lineplot(data=zip_data_sorted, x='zip_code', y='calls_per_1000', marker='o')

plt.title('2-1-1 Calls Per 1,000 Residents by ZIP Code')
plt.xlabel('ZIP Code')
plt.ylabel('Calls Per 1,000 Residents')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()