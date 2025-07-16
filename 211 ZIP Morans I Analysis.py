import geopandas as gpd
import pandas as pd
from esda.moran import Moran
import matplotlib.pyplot as plt
from esda.moran import Moran_Local
from splot.esda import lisa_cluster
from libpysal.weights import Queen
import numpy as np
np.random.seed(42)

# to open virtual environment: venv\Scripts\activate

'''
SPATIAL AUTOCORRELATION ANALYSIS

Morans I:
Morans I is a global measure of spatial autocorrelation.
It tells us whether ZIP codes with similar values tend to be 
spatially clustered (near each other) or randomly scattered.

We're applying Morans I to:
- Callers per 1,000 residents → to check if high-need ZIPs are geographically concentrated
- Poverty Rate → to see if high-poverty areas are spatially clustered
- ALICE Rate → to test spatial patterns among the working poor
- Average of Poverty + ALICE → to explore compound spatial disadvantage

We're also creating a Bivariate Morans I where we strictly cross reference Economic Instability 

Interpretation of Morans I:
- Positive values (near +1) → spatial clustering (similar ZIPs near each other)
- Zero (≈ 0) → random spatial pattern
- Negative (toward -1) → checkerboard pattern (highs near lows)

A statistically significant Morans I (p < 0.05) suggests that 
the variable is **not randomly distributed** across space.

Local Indicators of Spatial Association (LISA)
While Morans I gives us a single summary for the entire area,
LISA breaks that down **ZIP by ZIP**, identifying:

- High-High (HH): high values surrounded by high → spatial hotspots
- Low-Low (LL): low values surrounded by low → spatial cold spots
- High-Low (HL) / Low-High (LH): spatial outliers

We're running LISA for:
- Callers per 1,000 residents
- Poverty Rate, ALICE Rate, or combined

The output **LISA Cluster Map** visualizes ZIPs with significant spatial patterns,
helping us pinpoint where geographically targeted interventions may be needed.

Example use:
- A High-High ZIP might benefit from more 2-1-1 resources or partner support.
- A Low-High ZIP (cold ZIP surrounded by need) might be underutilizing services.

'''

geojson_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json'
gdf = gpd.read_file(geojson_url)
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

df = pd.read_csv("New_211_Client_Cleaned.csv")
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

# Morans I: Callers per 1,000 & ZIP
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]
gdf = gdf.merge(df[['zip_code', 'callers_per_1000']], on='zip_code')
w = Queen.from_dataframe(gdf)
w.transform = 'r'
y = gdf['callers_per_1000'].fillna(0).values
moran = Moran(y, w)
print(f"Moran's I: {moran.I:.4f}")
print(f"P-value (permutation): {moran.p_sim:.4f}")

# prep for economic instability Morans I
# load economic indicator data (poverty + ALICE)
# load economic indicator data (poverty + ALICE)
df_demo = pd.read_csv("211 Area Indicators_ZipZCTA.csv")
df_demo['zip_code'] = df_demo['GEO.display_label'].astype(str).str.extract(r'(\d{5})')

# select and rename relevant columns
# rename columns to match intended usage
df_demo = df_demo[['zip_code', 'Pct_Poverty_Households', 'Pct_Below.ALICE_Households']]
df_demo.columns = ['zip_code', 'poverty_rate', 'poverty_alice_sum']

# merge into GDF
gdf = gdf.merge(df_demo, on='zip_code', how='left')

gdf['alice_rate'] = gdf['poverty_alice_sum'] - gdf['poverty_rate']

# poverty
moran_pov = Moran(gdf['poverty_rate'].fillna(0).values, w)
print(f"[Poverty] Moran's I: {moran_pov.I:.4f}, p = {moran_pov.p_sim:.4f}")

# ALICE
moran_alice = Moran(gdf['alice_rate'].fillna(0).values, w)
print(f"[ALICE] Moran's I: {moran_alice.I:.4f}, p = {moran_alice.p_sim:.4f}")

# combo
moran_combo = Moran(gdf['poverty_alice_sum'].fillna(0).values, w)
print(f"[Poverty+ALICE] Moran's I: {moran_combo.I:.4f}, p = {moran_combo.p_sim:.4f}")


'''
RUNNING LISA FOR MORANS I ECONOMIC INSTABILITY
'''
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
plt.title("LISA Cluster Map: Economic Instability")
plt.tight_layout()
plt.show()
'''

'''
CODE FOR BIVARIATE MORANS I (ECONOMIC INSTABILITY & CALLER RATE) & VISUALS
'''
# !!!! ==== POVERTY & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

from esda.moran import Moran_Local_BV

biv_poverty = Moran_Local_BV(gdf['poverty_rate'], gdf['callers_per_1000'], w, permutations=999, seed=42)

# add results to GDF
gdf['biv_poverty_I'] = biv_poverty.Is
gdf['biv_poverty_p'] = biv_poverty.p_sim
gdf['biv_poverty_quadrant'] = biv_poverty.q
gdf['biv_poverty_sig'] = biv_poverty.p_sim < 0.05

# filter to significant results only
gdf_plot = gdf[gdf['biv_poverty_sig'] == True]

import matplotlib.patches as mpatches

quad_colors_POV = {
    1: '#CCCCCC',
    2: '#0A2F5A',
    3: '#CCCCCC',
    4: '#D22630'
}

quad_labels_POV = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_POV = [
    mpatches.Patch(color='#CCCCCC', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#CCCCCC', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color="#FFFFFF", label='Not Statistically Significant')
]

# create a new column with quadrant label
gdf['biv_poverty_label'] = gdf['biv_poverty_quadrant'].map(quad_labels_POV)
gdf['biv_poverty_color'] = gdf['biv_poverty_quadrant'].map(quad_colors_POV)

# apply color only if significant, else light gray
gdf['biv_poverty_final_color'] = gdf.apply(
    lambda row: row['biv_poverty_color'] if row['biv_poverty_sig'] else "#FFFFFF",
    axis=1
)

# plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_poverty_final_color'], linewidth=0.2, edgecolor='black', ax=ax)

ax.legend(
    handles=legend_elements_POV,
    loc='upper right',
    frameon=True,
    title='Bivariate LISA Cluster'
)

ax.set_title("Bivariate Local Moran's I:\nPoverty Rate vs Callers per 1,000 Residents", fontsize=14)
ax.axis('off')

plt.tight_layout()
plt.show()

# !!!! ==== ALICE & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

biv_alice = Moran_Local_BV(gdf['alice_rate'], gdf['callers_per_1000'], w, permutations=999, seed=42)

gdf['biv_alice_I'] = biv_alice.Is
gdf['biv_alice_p'] = biv_alice.p_sim
gdf['biv_alice_q'] = biv_alice.q
gdf['biv_alice_sig'] = biv_alice.p_sim < 0.05

quad_colors_ALICE = {
    1: '#CCCCCC',
    2: '#0A2F5A',
    3: '#CCCCCC',
    4: '#D22630'
}

quad_labels_ALICE = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_ALICE = [
    mpatches.Patch(color='#CCCCCC', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#CCCCCC', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color="#FFFFFF", label='Not Statistically Significant')
]

gdf['biv_alice_label'] = gdf['biv_alice_q'].map(quad_labels_ALICE)
gdf['biv_alice_color'] = gdf['biv_alice_q'].map(quad_colors_ALICE)

gdf['biv_alice_final_color'] = gdf.apply(
    lambda row: row['biv_alice_color'] if row['biv_alice_sig'] else "#FFFFFF",
    axis=1
)
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_alice_final_color'], linewidth=0.2, edgecolor='black', ax=ax)

ax.legend(handles=legend_elements_ALICE, loc='upper right', title='Bivariate LISA Cluster')
ax.set_title("Bivariate Local Moran's I:\nALICE Rate vs Callers per 1,000 Residents", fontsize=14)
ax.axis('off')

plt.tight_layout()
plt.show()

# !!!! ==== ALICE + POVERTY SUM & CALLER RATE CODE & VISUAL ==== !!!!

w = Queen.from_dataframe(gdf)
w.transform = 'r'

print(gdf[['poverty_alice_sum', 'callers_per_1000']].head())
print(gdf[['poverty_alice_sum', 'callers_per_1000']].isna().sum())

biv_combined = Moran_Local_BV(gdf['poverty_alice_sum'], gdf['callers_per_1000'], w, permutations=999, seed=42)

gdf['biv_comb_I'] = biv_combined.Is
gdf['biv_comb_p'] = biv_combined.p_sim
gdf['biv_comb_q'] = biv_combined.q
gdf['biv_comb_sig'] = biv_combined.p_sim < 0.05

quad_colors_COMBO = {
    1: '#CCCCCC',
    2: '#0A2F5A',
    3: '#CCCCCC',
    4: '#D22630'
}

quad_labels_COMBO = {
    1: 'HH: High Poverty–High Calls = Well Aligned',
    2: 'LH: Low Poverty–High Calls = Misaligned',
    3: 'LL: Low Poverty–Low Calls = Well Aligned',
    4: 'HL: High Poverty–Low Calls = Service Gap'
}

legend_elements_COMBO = [
    mpatches.Patch(color='#CCCCCC', label='HH: High Poverty–High Calls = Well Aligned'),
    mpatches.Patch(color='#D22630', label='HL: High Poverty–Low Calls = Service Gap'),
    mpatches.Patch(color='#0A2F5A', label='LH: Low Poverty–High Calls = Misaligned'),
    mpatches.Patch(color='#CCCCCC', label='LL: Low Poverty–Low Calls = Well Aligned'),
    mpatches.Patch(color="#FFFFFF", label='Not Statistically Significant')
]


gdf['biv_comb_label'] = gdf['biv_comb_q'].map(quad_labels_COMBO)
gdf['biv_comb_color'] = gdf['biv_comb_q'].map(quad_colors_COMBO)

gdf['biv_comb_final_color'] = gdf.apply(
    lambda row: row['biv_comb_color'] if row['biv_comb_sig'] else "#FFFFFF",
    axis=1
)

fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['biv_comb_final_color'], linewidth=0.2, edgecolor='black', ax=ax)

ax.legend(handles=legend_elements_COMBO, loc='upper right', title='Bivariate LISA Cluster')
ax.set_title("Bivariate Local Moran's I:\nBelow ALICE vs Callers per 1,000 Residents", fontsize=14)
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

moran_cols_sum = [
    'zip_code', 'poverty_alice_sum', 'callers_per_1000',
    'biv_comb_I', 'biv_comb_p',
    'biv_comb_q', 'biv_comb_sig', 'biv_comb_label'
]

gdf = gdf.reset_index(drop=True)

gdf[moran_cols_pov].to_csv('bivariate_data/Bivariate_Poverty_vs_CallerRate_LISA.csv', index=False)
gdf[moran_cols_alice].to_csv('bivariate_data/Bivariate_ALICE_vs_CallerRate_LISA.csv', index=False)
gdf[moran_cols_sum].to_csv('bivariate_data/Bivariate_PovertyALICE_vs_CallerRate_LISA.csv', index=False)
# merge total_callers from df into gdf before Moran filtering
gdf = gdf.merge(df[['zip_code', 'total_callers']], on='zip_code', how='left')
# poverty-based outliers (quadrants 2 and 4)
poverty_outliers = gdf[
    (gdf['biv_poverty_sig']) &
    (gdf['biv_poverty_quadrant'].isin([2, 4]))
]

poverty_out_table = poverty_outliers[[
    'zip_code',
    'callers_per_1000',
    'poverty_rate',
    'poverty_alice_sum',
    'total_callers',
    'biv_poverty_I',
    'biv_poverty_p'
]].copy()

# rename columns for clarity
poverty_out_table = poverty_out_table.rename(columns={
    'poverty_alice_sum': 'below_alice_rate',
    'biv_poverty_I': 'moran_I',
    'biv_poverty_p': 'p_value'
})

# export to csv
poverty_out_table.to_csv("Outlier_Poverty_Table.csv", index=False)

# combined poverty + ALICE outliers (quadrants 2 and 4)
combo_outliers = gdf[
    (gdf['biv_comb_sig']) &
    (gdf['biv_comb_q'].isin([2, 4]))
]

combo_out_table = combo_outliers[[
    'zip_code',
    'callers_per_1000',
    'poverty_rate',
    'poverty_alice_sum',
    'total_callers',
    'biv_comb_I',
    'biv_comb_p'
]].copy()

combo_out_table = combo_out_table.rename(columns={
    'poverty_alice_sum': 'below_alice_rate',
    'biv_comb_I': 'moran_I',
    'biv_comb_p': 'p_value'
})

combo_out_table.to_csv("Outlier_Below_ALICE_Table.csv", index=False)
