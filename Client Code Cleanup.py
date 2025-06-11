import pandas as pd


# to open virtual environment: venv\Scripts\activate


# === STEP 1: load CSV ===
df = pd.read_csv('211 Call Data_Client Tab_All Years.csv')


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

# preview the result
print("\nTop 10 ZIP codes by call count")
print(zip_counts.head(10))

zip_counts.to_csv('Calls_By_Zip.csv', index=False)

