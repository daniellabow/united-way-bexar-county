import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran_Local

# load ZIP caller rate data
df = pd.read_csv("New_211_Client_Cleaned.csv")
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

# load shapefile
gdf = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

# keep only ZIPs with caller data
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]

# merge in caller rate
gdf = gdf.merge(df[['zip_code', 'callers_per_1000']], on='zip_code', how='left')
gdf = gdf.dropna(subset=['callers_per_1000'])

w = Queen.from_dataframe(gdf)
w.transform = 'r'

# LISA on caller rate
lisa_callers = Moran_Local(gdf['callers_per_1000'].values, w, permutations=999, seed=42)

# store results
gdf['lisa_callers_q'] = lisa_callers.q
gdf['lisa_callers_p'] = lisa_callers.p_sim
gdf['lisa_callers_sig'] = gdf['lisa_callers_p'] < 0.05

gdf['lisa_callers_quad_label'] = gdf.apply(
    lambda row: {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}.get(row['lisa_callers_q']) if row['lisa_callers_sig'] else 'NS',
    axis=1
)

gdf[['zip_code', 'lisa_callers_q', 'lisa_callers_p', 'lisa_callers_sig', 'lisa_callers_quad_label']].to_csv(
    "final_efficient_chosen_tests/LISA_CallerRate_Results.csv", index=False
)

print("LISA Caller Rate complete! Results saved to 'LISA_CallerRate_Results.csv'")
