import pandas as pd

'''
This Python script processes and visualizes economic hardship data by ZIP code for the 2-1-1 Alamo Region.

It serves as a cleanup and preparation step for ZIP-level poverty and ALICE metrics using the 
'211 Area Indicators_ZipZCTA.csv' dataset provided by the nonprofit partner.

What it does:
- Extracts 5-digit ZIP codes and selects key columns: poverty rate and ALICE rate
- Creates a new column (`econ_instability`) which combines poverty + ALICE for a broader view of need
- Sorts and saves a list of top ZIP codes with the highest economic instability
- Produces three choropleth maps (poverty, ALICE, and combined instability) for geographic visualization

These outputs are useful for identifying ZIP codes facing the greatest economic hardship and will support 
further correlation and equity analysis in subsequent scripts (e.g., comparing 2-1-1 callers per ZIP to local need).

Note: This file does not handle 2-1-1 call data. It focuses exclusively on census-style indicators of economic instability.
'''

# load the cleaned ZIP indicator data
df = pd.read_csv('211 Area Indicators_ZipZCTA.csv')

# extract and clean relevant columns
df['zip_code'] = df['GEO.display_label'].astype(str).str.extract(r'(\d{5})')

df_econ = df[['zip_code', 'Pct_Poverty_Households', 'Pct_Below.ALICE_Households']]
df_econ.columns = ['zip_code', 'poverty_rate', 'alice_rate']

# create a combined instability score (just for ranking purposes)
df_econ['econ_instability'] = df_econ['poverty_rate'] + df_econ['alice_rate']

# sort by economic instability
top_instability = df_econ.sort_values(by='econ_instability', ascending=False)

# preview top ZIPs
print("Top 10 ZIPs by economic instability:")
print(top_instability.head(10))

# save to CSV
top_instability.to_csv('testing_backlog/Top_ZIPs_Economic_Instability.csv', index=False)
top_instability['zip_code'] = top_instability['zip_code'].astype(str).str.zfill(5)


import plotly.express as px
import matplotlib.pyplot as plt

'''
poverty_rate Definition:
This is the percentage of households in a ZIP code that are living below the federal poverty line.

A higher number here = more economic hardship in that area.

Example:

poverty_rate = 0.40 → 40% of households are in poverty

poverty_rate = 0.15 → 15% are in poverty
'''

# create choropleth map of poverty rate
fig = px.choropleth(
    df_econ,
    geojson='https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json',
    locations='zip_code',
    featureidkey='properties.ZCTA5CE10',
    color='poverty_rate',
    color_continuous_scale=['#e6eaf5', '#aab3df', '#6d7ec2', '#253791'],  # Light to UW Blue
    scope='usa',
    labels={'poverty_rate': 'Poverty Rate'},
    title='Poverty Rate by ZIP Code (2-1-1 Alamo Region)'
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()

# ALICE rate map
fig = px.choropleth(
    df_econ,
    geojson='https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json',
    locations='zip_code',
    featureidkey='properties.ZCTA5CE10',
    color='alice_rate',
    color_continuous_scale=['#fff4e0', '#ffd27a', '#fdb913', '#e29400'],  # Light to UW Yellow/Gold
    scope='usa',
    labels={'alice_rate': 'ALICE Rate'},
    title='ALICE Rate by ZIP Code (2-1-1 Alamo Region)'
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()

'''
alice_rate Definition:
This represents the percentage of households that are above poverty but below the ALICE threshold, meaning they:

Earn too much to qualify as "poverty"

But don't earn enough to meet basic cost-of-living needs (housing, food, childcare, etc.)

Higher alice_rate = More people living paycheck to paycheck or struggling to stay afloat 
'''


# poverty + ALICE
fig = px.choropleth(
    df_econ,
    geojson='https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json',
    locations='zip_code',
    featureidkey='properties.ZCTA5CE10',
    color='econ_instability',
    color_continuous_scale=['#fde3e6', '#f49ca1', '#e85c70', '#e21737'],  # Light to UW Red
    scope='usa',
    labels={'econ_instability': 'Poverty + ALICE Rate'},
    title='Economic Instability by ZIP Code (Poverty + ALICE)'
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig.show()

'''
econ_instability = poverty_rate + alice_rate
So this is a combined view of both:

Households in poverty and households in that financial gray area (ALICE)

Higher econ_instability = Overall more economic hardship in the area.
'''