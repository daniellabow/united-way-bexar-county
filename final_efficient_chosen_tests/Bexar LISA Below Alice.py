import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

# Load already-filtered Bexar ZIP-level data
df_demo = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df_demo['zip_code'] = df_demo['zip_code'].astype(str).str.zfill(5)

# Load Texas ZIP shapefile and filter for ZIPs in your data
gdf = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)
gdf = gdf[gdf['zip_code'].isin(df_demo['zip_code'])]

# Merge ALICE rate into GeoDataFrame
gdf = gdf.merge(df_demo[['zip_code', 'poverty_alice_sum']], on='zip_code', how='left')
gdf = gdf.dropna(subset=['poverty_alice_sum'])

# Create spatial weights using Queen contiguity
w = Queen.from_dataframe(gdf)
w.transform = 'r'

# Run local Moran’s I on ALICE rate
lisa_alice = Moran_Local(gdf['poverty_alice_sum'].values, w, permutations=999, seed=42)

# Store LISA results in the GeoDataFrame
gdf['lisa_alice_q'] = lisa_alice.q
gdf['lisa_alice_p'] = lisa_alice.p_sim
gdf['lisa_alice_sig'] = gdf['lisa_alice_p'] < 0.05

# Assign quadrant labels or 'NS'
gdf['lisa_alice_quad_label'] = gdf.apply(
    lambda row: {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}.get(row['lisa_alice_q']) if row['lisa_alice_sig'] else 'NS',
    axis=1
)

# Save results
gdf[['zip_code', 'lisa_alice_q', 'lisa_alice_p', 'lisa_alice_sig', 'lisa_alice_quad_label']].to_csv(
    "final_efficient_chosen_tests/LISA_Below_ALICE_Results.csv", index=False
)

print("LISA on Below ALICE complete. Results saved to 'LISA_Below_ALICE_Results.csv'")
