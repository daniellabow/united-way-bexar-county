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


# === STEP 3: Clean ZIP code column ===
# Replace 'zip_code' with the correct column name if it's different
#df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)


# === STEP 4: Count calls per ZIP code ===
#zip_counts = df['zip_code'].value_counts().reset_index()
#zip_counts.columns = ['zip_code', 'total_calls']


# === STEP 5: View top 10 ZIPs ===
#print("\nTop 10 ZIP codes by call volume:")
#print(zip_counts.head(10))


# === Optional: Export the results ===
