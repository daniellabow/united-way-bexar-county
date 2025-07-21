import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

df_demo = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df_demo['zip_code'] = df_demo['zip_code'].astype(str).str.zfill(5)

gdf = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)
gdf = gdf[gdf['zip_code'].isin(df_demo['zip_code'])]

gdf = gdf.merge(df_demo[['zip_code', 'poverty_alice_sum']], on='zip_code', how='left')
gdf = gdf.dropna(subset=['poverty_alice_sum'])

w = Queen.from_dataframe(gdf)
w.transform = 'r'

lisa_alice = Moran_Local(gdf['poverty_alice_sum'].values, w, permutations=999, seed=42)

gdf['lisa_alice_q'] = lisa_alice.q
gdf['lisa_alice_p'] = lisa_alice.p_sim
gdf['lisa_alice_sig'] = gdf['lisa_alice_p'] < 0.05

gdf['lisa_alice_quad_label'] = gdf.apply(
    lambda row: {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}.get(row['lisa_alice_q']) if row['lisa_alice_sig'] else 'NS',
    axis=1
)

gdf[['zip_code', 'lisa_alice_q', 'lisa_alice_p', 'lisa_alice_sig', 'lisa_alice_quad_label']].to_csv(
    "final_efficient_chosen_tests/BEXAR_LISA_Below_ALICE_Results.csv", index=False
)

print("LISA on Below ALICE complete! Results saved to 'BEXAR_LISA_Below_ALICE_Results.csv'")
