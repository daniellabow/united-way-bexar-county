import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

df_demo = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df_demo['zip_code'] = df_demo['zip_code'].astype(str).str.zfill(5)

gdf = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)
gdf = gdf[gdf['zip_code'].isin(df_demo['zip_code'])]

gdf = gdf.merge(df_demo[['zip_code', 'poverty_rate']], on='zip_code', how='left')
gdf = gdf.dropna(subset=['poverty_rate'])

w = Queen.from_dataframe(gdf)
w.transform = 'r'

lisa_poverty = Moran_Local(gdf['poverty_rate'].values, w, permutations=999, seed=42)

gdf['lisa_poverty_q'] = lisa_poverty.q
gdf['lisa_poverty_p'] = lisa_poverty.p_sim
gdf['lisa_poverty_sig'] = gdf['lisa_poverty_p'] < 0.05

gdf['lisa_poverty_quad_label'] = gdf.apply(
    lambda row: {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}.get(row['lisa_poverty_q']) if row['lisa_poverty_sig'] else 'NS',
    axis=1
)

# save LISA output for poverty
gdf[['zip_code', 'lisa_poverty_q', 'lisa_poverty_p', 'lisa_poverty_sig', 'lisa_poverty_quad_label']].to_csv(
    "final_efficient_chosen_tests/BEXAR_LISA_Poverty_Results.csv", index=False
)

print("LISA on Poverty complete! Results saved to 'BEXAR_LISA_Poverty_Results.csv'")
