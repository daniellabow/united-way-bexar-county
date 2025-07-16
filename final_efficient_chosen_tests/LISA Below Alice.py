import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

# load the ALICE rate data
df_demo = pd.read_csv("211 Area Indicators_ZipZCTA.csv")
df_demo['zip_code'] = df_demo['GEO.display_label'].astype(str).str.extract(r'(\d{5})')
df_demo = df_demo[['zip_code', 'Pct_Below.ALICE_Households']]
df_demo.columns = ['zip_code', 'alice_rate']

# load gdf
gdf = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

# keep zips only in the demo data
gdf = gdf[gdf['zip_code'].isin(df_demo['zip_code'])]

# merge ALICE into GDF
gdf = gdf.merge(df_demo, on='zip_code', how='left')
gdf = gdf.dropna(subset=['alice_rate'])

# spatial weights
w = Queen.from_dataframe(gdf)
w.transform = 'r'

# local Moran's I on below ALICE rate
lisa_alice = Moran_Local(gdf['alice_rate'].values, w, permutations=999, seed=42)

# store LISA results
gdf['lisa_alice_q'] = lisa_alice.q
gdf['lisa_alice_p'] = lisa_alice.p_sim
gdf['lisa_alice_sig'] = gdf['lisa_alice_p'] < 0.05

# add 'NS' label where LISA not significant
gdf['lisa_alice_quad_label'] = gdf.apply(
    lambda row: {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}.get(row['lisa_alice_q']) if row['lisa_alice_sig'] else 'NS',
    axis=1
)
# save LISA results for future use
gdf[['zip_code', 'lisa_alice_q', 'lisa_alice_p', 'lisa_alice_sig', 'lisa_alice_quad_label']].to_csv(
    "final_efficient_chosen_tests/LISA_Below_ALICE_Results.csv", index=False
)

print("LISA on Below ALICE complete. Results saved to 'LISA_Below_ALICE_Results.csv'")
