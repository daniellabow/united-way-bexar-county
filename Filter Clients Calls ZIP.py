import pandas as pd
import ast
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

'''
This Python file performs a similar role as 'Client ZIP Code Cleanup.py' but is specifically 
tailored for use in 'ZIP 211 Spearman Analysis.py'. I created this version after meeting 
with our nonprofit point of contact to support deeper geographic visualization and statistical testing.

In this file, we're being more thorough with the data cleaning, that includes:
- Removing postal ZIP codes
- Dropping any ZIP codes present in the call data but missing from the ZIP-level census data
- Filtering out call records marked as "Wrong #" or "Phantom" from the interaction data

That said, the original 'Client ZIP Code Cleanup.py' and its output CSVs are still important and useful — 
especially because they retain all call records (including "Wrong #" and "Phantom" entries). 
That broader data helps capture the full scope of caller volume, which may be valuable for 
operations, system diagnostics, or workload evaluation.
'''


# load the CSV files
df_client = pd.read_csv('211 Call Data_Client Tab_All Years.csv', low_memory=False)
df_area = pd.read_csv('211 Area Indicators_ZipZCTA.csv', low_memory=False)
df_interaction = pd.read_csv('211 Call Data_Interaction Tab_All Years.csv', low_memory=False)

# drop duplicate Client_Id to get unique callers
print("Before:", df_client.shape)
df_client_unique = df_client.drop_duplicates(subset=['Client_Id'])
print("After:", df_client_unique.shape)

'''
Now were cleaning out the ZIPS and ZIPS that were not listed in census data provided by nonprofit
'''
# extract 5-digit ZIP codes and standardize
df_client_unique.loc[:, 'zip_code'] = (
    df_client_unique['ClientAddressus_ClientAddressus_zip']
    .astype(str)
    .str.extract(r'(\d{5})')
)
# extract valid ZIPs from census data
df_area['zip_code'] = df_area['GEO.display_label'].astype(str).str.extract(r'(\d{5})')
valid_zips = df_area['zip_code'].dropna().unique()

# keep only callers from ZIPs present in the area indicators
df_client_valid = df_client_unique[df_client_unique['zip_code'].isin(valid_zips)]

'''
Now were cleaning duplicates of interaction ID
'''
# drop duplicate interactions by Interaction_Id
print("Before deduplication:", df_interaction.shape)
df_interaction = df_interaction.drop_duplicates(subset=['Interaction_Id'])
print("After deduplication:", df_interaction.shape)

'''
Now were cleaning out the call types
'''
# see raw call types before cleaning
print(df_interaction['InteractionOption_CallType'].value_counts())

# drop rows where call type is missing
df_interaction = df_interaction[df_interaction['InteractionOption_CallType'].notna()]

# convert call type to string (if needed)
df_interaction['InteractionOption_CallType'] = df_interaction['InteractionOption_CallType'].astype(str)

# safely parse and extract the first call type
def clean_call_type(val):
    try:
        parsed = ast.literal_eval(val)
        return parsed[0] if isinstance(parsed, list) and len(parsed) > 0 else None
    except:
        return None

df_interaction['clean_call_type'] = df_interaction['InteractionOption_CallType'].apply(clean_call_type)

# drop rows where parsing failed (i.e., call type is still None)
df_interaction = df_interaction[df_interaction['clean_call_type'].notna()]

'''
[Caller Filtering (done after call-level filtering but before removing bad calls)]
We dedupe to one call per caller, then remove 'Phantom' and 'Wrong #' here to accurately track loss of callers
'''

# keep only interactions from callers with valid ZIPs
df_interaction_valid_zip = df_interaction[df_interaction['Client_Id'].isin(df_client_valid['Client_Id'])]

# drop to one call per caller
df_one_call_per_caller = df_interaction_valid_zip.drop_duplicates(subset='Client_Id')
total_valid_zip_unique_callers = df_one_call_per_caller['Client_Id'].nunique()

# remove Phantom/Wrong # from that deduped set
bad_call_types = ['Phantom', 'Wrong #']
df_callers_final = df_one_call_per_caller[~df_one_call_per_caller['clean_call_type'].isin(bad_call_types)]
total_final_callers = df_callers_final['Client_Id'].nunique()

# Print a clear summary
print("\n[Caller Filtering Summary]")
print(f"Unique callers with valid ZIPs (before removing bad call types): {total_valid_zip_unique_callers}")
print(f"Callers remaining after removing 'Phantom' and 'Wrong #' call types: {total_final_callers}")
print(f"Callers excluded due to having only invalid call types: {total_valid_zip_unique_callers - total_final_callers}")

# filter out 'Phantom' and 'Wrong #' calls
bad_call_types = ['Phantom', 'Wrong #']
before_filtering = df_interaction.shape[0]
df_interaction = df_interaction[~df_interaction['clean_call_type'].isin(bad_call_types)]
after_filtering = df_interaction.shape[0]

# output filter summary
print(f"\nCalls before filtering: {before_filtering}")
print(f"Calls after filtering: {after_filtering}")
print(f"Bad calls removed: {before_filtering - after_filtering}")


'''
Finally tying everything together into one new csv
'''

# use the cleaned caller list from earlier (after filtering Phantom/Wrong #)
valid_client_ids = df_callers_final['Client_Id'].unique()
final_callers = df_client_valid[df_client_valid['Client_Id'].isin(valid_client_ids)]

# count unique callers by ZIP
zip_counts = final_callers['zip_code'].value_counts().reset_index()
zip_counts.columns = ['zip_code', 'total_callers']

# save final cleaned ZIP-level callers CSV
zip_counts.to_csv('New_211_Client_Cleaned.csv', index=False)

# preview top rows
print("\nTop ZIPs by total unique callers:")
print(zip_counts.head(10))

'''
Now what we need specifically for the Spearmens code later on is a rate, the following is that code for the CSV
We're pulling from ZIP-level population and calculating callers per 1,000 residents
'''

# count unique callers by ZIP
zip_counts = final_callers['zip_code'].value_counts().reset_index()
zip_counts.columns = ['zip_code', 'total_callers']

# get ZIP population
zip_pop = df_area[['zip_code', 'Pop_Estimate']].dropna()
zip_pop.columns = ['zip_code', 'population']

# merge caller counts with population
zip_data = pd.merge(zip_counts, zip_pop, on='zip_code', how='left')

# fill missing population with 1 to avoid divide-by-zero
zip_data['population'] = zip_data['population'].fillna(1)

# calc callers per 1,000 residents
zip_data['callers_per_1000'] = (zip_data['total_callers'] / zip_data['population']) * 1000

# save final cleaned and enriched dataset
zip_data.to_csv('New_211_Client_Cleaned.csv', index=False)

# preview top ZIPs
print("\nTop ZIPs by callers per 1,000 residents:")
print(zip_data.sort_values(by='callers_per_1000', ascending=False).head(10))

'''
FINALLY, lets visualize all this scrumptious code
'''

# load ZIP-level shapefile/GeoJSON
geojson_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json'
gdf = gpd.read_file(geojson_url)
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

# merge with 2-1-1 ZIP data
df_map = pd.read_csv('New_211_Client_Cleaned.csv')
df_map['zip_code'] = df_map['zip_code'].astype(str).str.zfill(5)

gdf = gdf[gdf['zip_code'].isin(df_map['zip_code'])]
gdf = gdf.merge(df_map, on='zip_code')


# !!!! ==== MAP callers per 1,000 ==== !!!!

# custom bin edges for callers per 1,000
rate_bins = [0, 42, 66, 133, 1000, float('inf')]
rate_labels = ['8-42', '42-66', '66-133', '133-1000', '>1000']

# apply manual binning to callers per 1,000
gdf['rate_quartile'] = pd.cut(gdf['callers_per_1000'], bins=rate_bins, labels=rate_labels, include_lowest=True)

# define color palette using label strings as keys
quartile_colors = {
    '8-42': '#A7D2FF',
    '42-66': '#5082F0',
    '66-133': '#0044B5',
    '133-1000': '#21296B',
    '>1000': "#00095B"
}

gdf['rate_color'] = gdf['rate_quartile'].map(quartile_colors)

fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['rate_color'], edgecolor='white', linewidth=0.3, ax=ax)
ax.set_title('2-1-1 Callers per 1,000 Residents by ZIP Code', fontsize=16)
ax.set_axis_off()

# legend
unique_rate_quartiles = gdf[['rate_quartile']].drop_duplicates().sort_values(by='rate_quartile')
rate_legend_elements = [
    mpatches.Patch(color=quartile_colors[label], label=label)
    for label in unique_rate_quartiles['rate_quartile']
]
ax.legend(handles=rate_legend_elements, title='Callers per 1,000 (Quartiles)', loc='upper right')

plt.tight_layout()
plt.show()


# !!!! ==== MAP total callers ==== !!!!

# apply manual binning to total callers (same bins and labels)
gdf['count_quartile'] = pd.cut(gdf['total_callers'], bins=rate_bins, labels=rate_labels, include_lowest=True)

# define count quartile bins (automated) and get actual bin edge
count_quartiles, count_bins = pd.qcut(
    gdf['total_callers'],
    4,
    retbins=True,
    duplicates='drop'
)

# create readable labels based on bin edges
count_labels = [f"{int(count_bins[i])}–{int(count_bins[i+1])}" for i in range(len(count_bins)-1)]

# apply quartile labels with actual ranges
gdf['count_quartile'] = pd.qcut(gdf['total_callers'], 4, labels=count_labels, duplicates='drop')

# define new color palette
count_quartile_colors = dict(zip(count_labels, ['#A7D2FF', '#5082F0', '#0044B5', '#21296B']))

# assign color for each ZIP
gdf['count_color'] = gdf['count_quartile'].map(count_quartile_colors)


fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['count_color'], edgecolor='white', linewidth=0.3, ax=ax)
ax.set_title('Total 2-1-1 Callers by ZIP Code', fontsize=16)
ax.set_axis_off()

# legend
unique_count_quartiles = gdf[['count_quartile']].drop_duplicates().sort_values(by='count_quartile')
count_legend_elements = [
    mpatches.Patch(color=count_quartile_colors[label], label=label)
    for label in unique_count_quartiles['count_quartile']
]
ax.legend(handles=count_legend_elements, title='Total Callers (Quartiles)', loc='upper right')

plt.tight_layout()
plt.show()
