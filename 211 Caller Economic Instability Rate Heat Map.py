import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.patches as mpatches
import geopandas as gpd

# to open virtual environment: venv\Scripts\activate

# load cleaned ZIP-level caller data
df_callers = pd.read_csv('New_211_Client_Cleaned.csv')
df_callers['zip_code'] = df_callers['zip_code'].astype(str).str.zfill(5)

# load ZIP-level demographic indicators (Poverty & ALICE)
df_demo = pd.read_csv('211 Area Indicators_ZipZCTA.csv', low_memory=False)
df_demo['zip_code'] = df_demo['GEO.display_label'].astype(str).str.extract(r'(\d{5})')
df_demo = df_demo[['zip_code', 'Pct_Poverty_Households', 'Pct_Below.ALICE_Households']]
df_demo.columns = ['zip_code', 'poverty_rate', 'alice_rate']

# merge both datasets on ZIP code
df = pd.merge(df_callers, df_demo, on='zip_code', how='inner')

# drop any rows with missing values just in case
df = df.dropna(subset=['callers_per_1000', 'poverty_rate', 'alice_rate'])

# add correct combo for sum, not avg
df['poverty_alice_sum'] = df['poverty_rate'] + df['alice_rate']



# !!!! ==== POVERTY RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!
df['poverty_quartile'] = pd.qcut(df['poverty_rate'], 4, labels=[1, 2, 3, 4])
df['caller_rate_quartile'] = pd.qcut(df['callers_per_1000'], 4, labels=[1, 2, 3, 4])

color_matrix = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]

# empty 4x4 count grid
count_grid = np.zeros((4, 4), dtype=int)

# count loop (adjusted for 4 quantiles)
for _, row in df.iterrows():
    x = int(row["poverty_quartile"]) - 1
    y = 4 - int(row["caller_rate_quartile"])  # reverse Y
    count_grid[y, x] += 1

# plot
fig, ax = plt.subplots(figsize=(7, 6))
for y in range(4):
    for x in range(4):
        facecolor = color_matrix[y][x]
        
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=facecolor,
            edgecolor='black',
            linewidth=1
        ))
        
        count = count_grid[y, x]
        percent = (count / len(df)) * 100
        text_color = 'white' if facecolor in ['#21296B', '#D12626'] else 'black'

        ax.text(
            x + 0.5, y + 0.5, f"{percent:.1f}%",
            va='center', ha='center',
            color=text_color,
            fontsize=10
            )

ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.set_xticks(np.arange(4) + 0.5)
ax.set_yticks(np.arange(4) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4'])
ax.set_yticklabels(['4', '3', '2', '1'])
ax.set_xlabel("Poverty Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & Poverty Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!

df["alice_quartile"] = pd.qcut(df["alice_rate"], 4, labels=[1, 2, 3, 4])
df["caller_quartile"] = pd.qcut(df["callers_per_1000"], 4, labels=[1, 2, 3, 4])

alice_grid = np.zeros((4, 4), dtype=int)

for _, row in df.iterrows():
    x = int(row["alice_quartile"]) - 1
    y = 4 - int(row["caller_quartile"])  # 4 - since we're in a 4x4 grid
    alice_grid[y, x] += 1

color_matrix_alice = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]

# plot heatmap
fig, ax = plt.subplots(figsize=(7, 6))

for y in range(4):
    for x in range(4):
        facecolor = color_matrix_alice[y][x]
        
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=facecolor,
            edgecolor='black',
            linewidth=1
        ))
        count = alice_grid[y, x]
        percent = (count / len(df)) * 100
        text_color = 'white' if facecolor in ['#21296B', '#D12626'] else 'black'

        ax.text(
            x + 0.5, y + 0.5, f"{percent:.1f}%",
            va='center', ha='center',
            color=text_color,
            fontsize=10
            )

ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.set_xticks(np.arange(4) + 0.5)
ax.set_yticks(np.arange(4) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4'])
ax.set_yticklabels(['4', '3', '2', '1'])  # Top to bottom
ax.set_xlabel("ALICE Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & ALICE Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

# !!!! ==== POVERTY + ALICE SUM vs CALLERS PER 1000 HEAT MAP ==== !!!!
df["sum_quartile"] = pd.qcut(df["poverty_alice_sum"], 4, labels=[1, 2, 3, 4])
df["caller_quartile"] = pd.qcut(df["callers_per_1000"], 4, labels=[1, 2, 3, 4])

sum_grid = np.zeros((4, 4), dtype=int)

for _, row in df.iterrows():
    x = int(row["sum_quartile"]) - 1
    y = 4 - int(row["caller_quartile"])  # reverse Y for top-bottom
    sum_grid[y, x] += 1

color_matrix_sum = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]

# plot
fig, ax = plt.subplots(figsize=(7, 6))

for y in range(4):
    for x in range(4):
        facecolor = color_matrix_sum[y][x]
        
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=facecolor,
            edgecolor='black',
            linewidth=1
        ))
        
        count = sum_grid[y, x]
        percent = (count / len(df)) * 100
        text_color = 'white' if facecolor in ['#21296B', '#D12626'] else 'black'

        ax.text(
            x + 0.5, y + 0.5, f"{percent:.1f}%",
            va='center', ha='center',
            color=text_color,
            fontsize=10
            )

ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.set_xticks(np.arange(4) + 0.5)
ax.set_yticks(np.arange(4) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4'])
ax.set_yticklabels(['4', '3', '2', '1'])  # top to bottom
ax.set_xlabel("Poverty + ALICE Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & Economic Instability Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

'''
NOW WE'RE TAKING THIS SAME CODE AND USING THE CATEGORIES WE HAVE PLACED EACH ZIP CODE INTO
AND REFLECTING THAT INFO BY COLOR CODING THE ZIPS ON A MAP

THE FOLLOWING CODE IS JUST THAT

'''
# combine quartile positions into a tuple (y, x) format
df['bivariate_cell'] = list(zip(
    4 - df['caller_rate_quartile'].astype(int),  # y = reversed caller quartile
    df['poverty_quartile'].astype(int) - 1        # x = poverty quartile (0-based)
))
# define the color matrix again for mapping
color_matrix = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]

# flatten it to a dict mapping (y, x) → color
color_dict = {(y, x): color_matrix[y][x] for y in range(4) for x in range(4)}

# assign each ZIP its color
df['bivariate_color'] = df['bivariate_cell'].map(color_dict)
# load ZIP shapefile / GeoJSON
geojson_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json'
gdf = gpd.read_file(geojson_url)
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)

# merge with df that now has bivariate_color
gdf = gdf.merge(df[['zip_code', 'bivariate_color']], on='zip_code', how='left')
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]

legend_labels = {
    (3, 3): 'HL: High Poverty – Low Calls',
    (3, 2): 'High Poverty – Med-Low Calls',
    (0, 0): 'LL: Low Poverty – Low Calls',
    (0, 1): 'Low Poverty – Med-High Calls',
    (0, 3): 'LH: Low Poverty – High Calls',
    (1, 0): 'Med-Low Poverty – High Calls',
    (1, 1): 'Neutral',
    (2, 3): 'Med-High Poverty – Low Calls'
}
legend_colors = {
    (3, 3): '#D12626',   # HL
    (3, 2): '#F47925',
    (0, 0): '#CCCCCC',   # LL
    (0, 1): '#5082F0',
    (0, 3): '#21296B',   # LH
    (1, 0): '#5082F0',
    (1, 1): '#CCCCCC',
    (2, 3): '#F47925'
}


legend_elements = [
    mpatches.Patch(color='#D12626', label='HL: High Poverty – Low Calls'),
    mpatches.Patch(color='#F47925', label='High Poverty – Medium-Low Calls'),
    mpatches.Patch(color='#21296B', label='LH: Low Poverty – High Calls'),
    mpatches.Patch(color='#5082F0', label='Low Poverty – Medium-High Calls'),
    mpatches.Patch(color='#CCCCCC', label='Neutral / In-Between')
]

# deduplicate legend entries by color
unique_legends = {}
for key, color in legend_colors.items():
    label = legend_labels[key]
    if color not in unique_legends:
        unique_legends[color] = label

legend_elements = [
    mpatches.Patch(color=color, label=label)
    for color, label in unique_legends.items()
]


# plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['bivariate_color'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)

ax.set_title("ZIP Map by Caller Rate & Poverty Quartile Bivariate Category")
ax.axis('off')
ax.legend(handles=legend_elements, loc='upper right', title='Bivariate Categories')
plt.tight_layout()
plt.show()

'''
NOW WE'RE DOING THE SAME THING BUT WITH ALICE RATE
AND CALLERS PER 1000
'''
# combine quartile positions into a tuple (y, x) format
df['bivariate_cell_alice'] = list(zip(
    4 - df['caller_quartile'].astype(int),  # y = reversed caller quartile
    df['alice_quartile'].astype(int) - 1     # x = alice quartile (0-based)
))
# define the color matrix again for mapping
color_matrix_alice = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]
# flatten it to a dict mapping (y, x) → color
color_dict_alice = {(y, x): color_matrix_alice[y][x] for y in range(4) for x in range(4)}
# assign each ZIP its color
df['bivariate_color_alice'] = df['bivariate_cell_alice'].map(color_dict_alice)
# merge with gdf that now has bivariate_color_alice
gdf = gdf.merge(df[['zip_code', 'bivariate_color_alice']], on='zip_code', how='left')
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]
legend_labels_alice = {
    (3, 3): 'HL: High ALICE – Low Calls',
    (3, 2): 'High ALICE – Med-Low Calls',
    (0, 0): 'LL: Low ALICE – Low Calls',
    (0, 1): 'Low ALICE – Med-High Calls',
    (0, 3): 'LH: Low ALICE – High Calls',
    (1, 0): 'Med-Low ALICE – High Calls',
    (1, 1): 'Neutral',
    (2, 3): 'Med-High ALICE – Low Calls'
}
legend_colors_alice = {
    (3, 3): '#D12626',   # HL
    (3, 2): '#F47925',
    (0, 0): '#CCCCCC',   # LL
    (0, 1): '#5082F0',
    (0, 3): '#21296B',   # LH
    (1, 0): '#5082F0',
    (1, 1): '#CCCCCC',
    (2, 3): '#F47925'
}
legend_elements_alice = [
    mpatches.Patch(color='#D12626', label='HL: High ALICE – Low Calls'),
    mpatches.Patch(color='#F47925', label='High ALICE – Medium-Low Calls'),
    mpatches.Patch(color='#21296B', label='LH: Low ALICE – High Calls'),
    mpatches.Patch(color='#5082F0', label='Low ALICE – Medium-High Calls'),
    mpatches.Patch(color='#CCCCCC', label='Neutral / In-Between')
]   
# deduplicate legend entries by color
unique_legends_alice = {}
for key, color in legend_colors_alice.items():
    label = legend_labels_alice[key]
    if color not in unique_legends_alice:
        unique_legends_alice[color] = label

legend_elements_alice = [
    mpatches.Patch(color=color, label=label)
    for color, label in unique_legends_alice.items()
]
# plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['bivariate_color_alice'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)
ax.set_title("ZIP Map by Caller Rate & ALICE Quartile Bivariate Category")
ax.axis('off')
ax.legend(handles=legend_elements_alice, loc='upper right', title='Bivariate Categories')
plt.tight_layout()
plt.show()

'''
NOW WE'RE DOING THE SAME THING BUT WITH POVERTY + ALICE SUM
AND CALLERS PER 1000    
'''
# combine quartile positions into a tuple (y, x) format
df['bivariate_cell_sum'] = list(zip(
    4 - df['caller_quartile'].astype(int),  # y = reversed caller quartile
    df['sum_quartile'].astype(int) - 1       # x = sum quartile (0-based)
))
# define the color matrix again for mapping
color_matrix_sum = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]
# flatten it to a dict mapping (y, x) → color
color_dict_sum = {(y, x): color_matrix_sum[y][x] for y in range(4) for x in range(4)}
# assign each ZIP its color
df['bivariate_color_sum'] = df['bivariate_cell_sum'].map(color_dict_sum)
# merge with gdf that now has bivariate_color_sum
gdf = gdf.merge(df[['zip_code', 'bivariate_color_sum']], on='zip_code', how='left')
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]
legend_labels_sum = {
    (3, 3): 'HL: High Economic Instability – Low Calls',
    (3, 2): 'High Economic Instability – Med-Low Calls',
    (0, 0): 'LL: Low Economic Instability – Low Calls',
    (0, 1): 'Low Economic Instability – Med-High Calls',
    (0, 3): 'LH: Low Economic Instability – High Calls',
    (1, 0): 'Med-Low Economic Instability – High Calls',
    (1, 1): 'Neutral',
    (2, 3): 'Med-High Economic Instability – Low Calls'
}
legend_colors_sum = {
    (3, 3): '#D12626',   # HL
    (3, 2): '#F47925',
    (0, 0): '#CCCCCC',   # LL
    (0, 1): '#5082F0',
    (0, 3): '#21296B',   # LH
    (1, 0): '#5082F0',
    (1, 1): '#CCCCCC',
    (2, 3): '#F47925'
}
legend_elements_sum = [
    mpatches.Patch(color='#D12626', label='HL: High Economic Instability – Low Calls'),
    mpatches.Patch(color='#F47925', label='High Economic Instability – Medium-Low Calls'),
    mpatches.Patch(color='#21296B', label='LH: Low Economic Instability – High Calls'),
    mpatches.Patch(color='#5082F0', label='Low Economic Instability – Medium-High Calls'),
    mpatches.Patch(color='#CCCCCC', label='Neutral / In-Between')
]
# deduplicate legend entries by color 
unique_legends_sum = {}
for key, color in legend_colors_sum.items():
    label = legend_labels_sum[key]
    if color not in unique_legends_sum:
        unique_legends_sum[color] = label

legend_elements_sum = [
    mpatches.Patch(color=color, label=label)
    for color, label in unique_legends_sum.items()
]
# plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['bivariate_color_sum'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)
ax.set_title("ZIP Map by Caller Rate & Economic Instability Rate Bivariate Category")
ax.axis('off')
ax.legend(handles=legend_elements_sum, loc='upper right', title='Bivariate Categories')
plt.tight_layout()
plt.show()
