import pandas as pd
import geopandas as gpd
from esda.moran import Moran
import matplotlib.pyplot as plt
from esda.moran import Moran_Local
from splot.esda import lisa_cluster
from libpysal.weights import Queen
'''
!!!!!! ====== BEXAR COUNTY ZIP CODE CLEANED DATASET ====== !!!!!!
This script loads the cleaned 211 caller data, extracts ZIP codes, and merges it with county
information from the original dataset. It filters the data to only include Bexar County ZIP codes and saves the cleaned dataset to a new CSV file.
The resulting dataset contains caller information along with the corresponding county, specifically for Bexar County ZIP codes.
This is useful for further analysis or visualization focused on Bexar County.
'''

# to open virtual environment: venv\Scripts\activate

# load your cleaned dataset with ZIP codes
df_clean = pd.read_csv('New_211_Client_Cleaned.csv')
df_clean['zip_code'] = df_clean['zip_code'].astype(str).str.zfill(5)

# area indicators with county + economic data
df_demo = pd.read_csv("211 Area Indicators_ZipZCTA.csv")
df_demo['zip_code'] = df_demo['Zip_Name'].astype(str).str.zfill(5)

# keep ZIP + county for filtering
df_county_ref = df_demo[['zip_code', 'County_Name']].dropna().drop_duplicates()
df_county_ref = df_county_ref.rename(columns={'County_Name': 'county'})

# merge county info into client data
df_merged = df_clean.merge(df_county_ref, on='zip_code', how='left')

# filter only Bexar County
df_bexar = df_merged[df_merged['county'].str.lower() == 'bexar'].copy()
df_bexar['county'] = 'Bexar'

# save Bexar-only data
df_bexar.to_csv('bexar_specific/Bexar_County_Cleaned_ZIP_Data.csv', index=False)

'''
     The following code is map prep for the Moran's I test
     (restricted to ZIPs listed in 'Bexar_County_Cleaned_ZIP_Data.csv')
'''

# prep economic indicator data
df_econ = df_demo[['zip_code', 'Pct_Poverty_Households', 'Pct_Below.ALICE_Households']].copy()
df_econ = df_econ.rename(columns={
    'Pct_Poverty_Households': 'poverty_rate',
    'Pct_Below.ALICE_Households': 'alice_rate'
})

# merge indicators into Bexar-only dataset
df_final = df_bexar.merge(df_econ, on='zip_code', how='left')

# save final output for spatial analysis
df_final.to_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv', index=False)


'''
     This is the end of Morans I bexar county map prep
'''


'''
Now that we have the cleaned Bexar County ZIP dataset, we're going to apply the same Morans I analysis as we did in the 211 ZIP Morans I Analysis script.
This will allow us to visualize the spatial distribution of 211 callers in specifically Bexar County,

                    REPLACE CSV's WITH: 'Bexar_County_ZIP_Eco_Indicator_Data.csv'

                    THE FOLLOWING CODE WILL RUN MORANS I ANALYSIS ON BEXAR COUNTY ZIP DATA
                    AND GENERATE VISUALS FOR POVERTY, ALICE, AND CALLER RATE
'''

# to open virtual environment: venv\Scripts\activate

# load your cleaned Bexar dataset
df = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

# load TX ZIP shapefile
geojson_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json'
gdf = gpd.read_file(geojson_url)
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

# merge and FILTER to Bexar ZIPs
gdf = gdf.merge(df, on='zip_code', how='left')
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]  # only Bexar ZIPs with data

# pov alice sum
gdf['poverty_alice_sum'] = gdf['poverty_rate'] + gdf['alice_rate']

w = Queen.from_dataframe(gdf)
w.transform = 'r'

# run Morans I
# callers per 1,000
moran_callers = Moran(gdf['callers_per_1000'].fillna(0).values, w)
print(f"[Callers/1000] Moran's I: {moran_callers.I:.4f}, p = {moran_callers.p_sim:.4f}")

# poverty Rate
moran_pov = Moran(gdf['poverty_rate'].fillna(0).values, w)
print(f"[Poverty] Moran's I: {moran_pov.I:.4f}, p = {moran_pov.p_sim:.4f}")

# ALICE Rate
moran_alice = Moran(gdf['alice_rate'].fillna(0).values, w)
print(f"[ALICE] Moran's I: {moran_alice.I:.4f}, p = {moran_alice.p_sim:.4f}")

# sum
moran_combo = Moran(gdf['poverty_alice_sum'].fillna(0).values, w)
print(f"[Poverty+ALICE] Moran's I: {moran_combo.I:.4f}, p = {moran_combo.p_sim:.4f}")

'''
RUNNING LISA FOR MORANS I ECONOMIC INSTABILITY - COMMENT OUT FOR TIME PURPOSES ONCE VISUALS ARE MADE
'''

# LISA for callers per 1,000
lisa_callers = Moran_Local(gdf['callers_per_1000'].fillna(0).values, w)
fig, ax = lisa_cluster(lisa_callers, gdf, p=0.05)
plt.title("LISA Cluster Map: Callers per 1,000")
plt.tight_layout()
plt.show()

# LISA for poverty rate
lisa_pov = Moran_Local(gdf['poverty_rate'].fillna(0).values, w)
fig, ax = lisa_cluster(lisa_pov, gdf, p=0.05)
plt.title("LISA Cluster Map: Poverty Rate")
plt.tight_layout()
plt.show()

# LISA for ALICE rate
lisa_alice = Moran_Local(gdf['alice_rate'].fillna(0).values, w)
fig, ax = lisa_cluster(lisa_alice, gdf, p=0.05)
plt.title("LISA Cluster Map: ALICE Rate")
plt.tight_layout()
plt.show()

# LISA for poverty + ALICE (sum)
lisa_combo = Moran_Local(gdf['poverty_alice_sum'].fillna(0).values, w)
fig, ax = lisa_cluster(lisa_combo, gdf, p=0.05)
plt.title("LISA Cluster Map: Economic Insability")
plt.tight_layout()
plt.show()


'''
CODE FOR BIVARIATE MORANS I (ECONOMIC INSTABILITY & CALLER RATE) & VISUALS
'''
# !!!! ==== POVERTY & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

from esda.moran import Moran_Local_BV

biv_poverty = Moran_Local_BV(gdf['poverty_rate'], gdf['callers_per_1000'], w)

# add results to GDF
gdf['biv_poverty_I'] = biv_poverty.Is
gdf['biv_poverty_p'] = biv_poverty.p_sim
gdf['biv_poverty_quadrant'] = biv_poverty.q
gdf['biv_poverty_sig'] = biv_poverty.p_sim < 0.05

# filter to significant results only
gdf_plot = gdf[gdf['biv_poverty_sig'] == True]

import matplotlib.patches as mpatches

quad_colors_POV = {
    1: '#FFD100',
    2: '#0A2F5A',
    3: '#93BAE9',
    4: '#D22630'
}

quad_labels_POV = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_POV = [
    mpatches.Patch(color='#FFD100', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#93BAE9', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color='#E0E0E0', label='Not Statistically Significant')
]

# create a new column with quadrant label
gdf['biv_poverty_label'] = gdf['biv_poverty_quadrant'].map(quad_labels_POV)
gdf['biv_poverty_color'] = gdf['biv_poverty_quadrant'].map(quad_colors_POV)

# apply color only if significant, else light gray
gdf['biv_poverty_final_color'] = gdf.apply(
    lambda row: row['biv_poverty_color'] if row['biv_poverty_sig'] else '#E0E0E0',
    axis=1
)

# plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_poverty_final_color'], linewidth=0.2, edgecolor='white', ax=ax)

ax.legend(
    handles=legend_elements_POV,
    loc='upper right',
    frameon=True,
    title='Bivariate LISA Cluster'
)

ax.set_title("Bivariate Spatial Clustering:\nPoverty Rate vs Callers per 1,000 Residents", fontsize=14)
ax.axis('off')

plt.tight_layout()
plt.show()

# !!!! ==== ALICE & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

biv_alice = Moran_Local_BV(gdf['alice_rate'], gdf['callers_per_1000'], w)

gdf['biv_alice_I'] = biv_alice.Is
gdf['biv_alice_p'] = biv_alice.p_sim
gdf['biv_alice_q'] = biv_alice.q
gdf['biv_alice_sig'] = biv_alice.p_sim < 0.05

quad_colors_ALICE = {
    1: '#FFD100',
    2: '#0A2F5A',
    3: '#93BAE9',
    4: '#D22630'
}

quad_labels_ALICE = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_ALICE = [
    mpatches.Patch(color='#FFD100', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#93BAE9', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color='#E0E0E0', label='Not Statistically Significant')
]

gdf['biv_alice_label'] = gdf['biv_alice_q'].map(quad_labels_ALICE)
gdf['biv_alice_color'] = gdf['biv_alice_q'].map(quad_colors_ALICE)

gdf['biv_alice_final_color'] = gdf.apply(
    lambda row: row['biv_alice_color'] if row['biv_alice_sig'] else '#E0E0E0',
    axis=1
)
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_alice_final_color'], linewidth=0.2, edgecolor='white', ax=ax)

ax.legend(handles=legend_elements_ALICE, loc='upper right', title='Bivariate LISA Cluster')
ax.set_title("Bivariate Spatial Clustering:\nALICE Rate vs Callers per 1,000 Residents", fontsize=14)
ax.axis('off')

plt.tight_layout()
plt.show()

# !!!! ==== ALICE + POVERTY SUM & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

gdf['poverty_alice_sum'] = gdf['poverty_rate'] + gdf['alice_rate']

print(gdf[['poverty_alice_sum', 'callers_per_1000']].head())
print(gdf[['poverty_alice_sum', 'callers_per_1000']].isna().sum())

biv_combined = Moran_Local_BV(gdf['poverty_alice_sum'], gdf['callers_per_1000'], w)

gdf['biv_comb_I'] = biv_combined.Is
gdf['biv_comb_p'] = biv_combined.p_sim
gdf['biv_comb_q'] = biv_combined.q
gdf['biv_comb_sig'] = biv_combined.p_sim < 0.05

quad_colors_COMBO = {
    1: '#FFD100',
    2: '#0A2F5A',
    3: '#93BAE9',
    4: '#D22630'
}

quad_labels_COMBO = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_COMBO = [
    mpatches.Patch(color='#FFD100', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#93BAE9', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color='#E0E0E0', label='Not Statistically Significant')
]


gdf['biv_comb_label'] = gdf['biv_comb_q'].map(quad_labels_COMBO)
gdf['biv_comb_color'] = gdf['biv_comb_q'].map(quad_colors_COMBO)

gdf['biv_comb_final_color'] = gdf.apply(
    lambda row: row['biv_comb_color'] if row['biv_comb_sig'] else '#E0E0E0',
    axis=1
)

fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_comb_final_color'], linewidth=0.2, edgecolor='white', ax=ax)

ax.legend(handles=legend_elements_COMBO, loc='upper right', title='Bivariate LISA Cluster')
ax.set_title("Bivariate Spatial Clustering:\nEconomic Instability vs Callers per 1,000 Residents", fontsize=14)
ax.axis('off')

plt.tight_layout()
plt.show()


'''
PRINT DIFF P AND RHO VALS
'''

moran_cols_pov = [
    'zip_code', 'poverty_rate', 'callers_per_1000',
    'biv_poverty_I', 'biv_poverty_p',
    'biv_poverty_quadrant', 'biv_poverty_sig', 'biv_poverty_label'
]

moran_cols_alice = [
    'zip_code', 'alice_rate', 'callers_per_1000',
    'biv_alice_I', 'biv_alice_p',
    'biv_alice_q', 'biv_alice_sig', 'biv_alice_label'
]

moran_cols_combo = [
    'zip_code', 'poverty_alice_sum', 'callers_per_1000',
    'biv_comb_I', 'biv_comb_p',
    'biv_comb_q', 'biv_comb_sig', 'biv_comb_label'
]

gdf = gdf.reset_index(drop=True)

gdf[moran_cols_pov].to_csv('bexar_specific/Bexar_Bivariate_Poverty_LISA.csv', index=False)
gdf[moran_cols_alice].to_csv('bexar_specific/Bexar_Bivariate_ALICE_LISA.csv', index=False)
gdf[moran_cols_combo].to_csv('bexar_specific/Bexar_Bivariate_Sum_LISA.csv', index=False)