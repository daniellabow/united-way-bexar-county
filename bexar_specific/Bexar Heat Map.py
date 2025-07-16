import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.patches as mpatches
import geopandas as gpd
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker, DrawingArea
from matplotlib.patches import Rectangle
import os

# to open virtual environment: venv\Scripts\activate

# load cleaned ZIP-level caller data
df = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

df['alice_rate'] = df['poverty_alice_sum'] - df['poverty_rate']

# drop any rows with missing values just in case
df = df.dropna(subset=['callers_per_1000', 'poverty_rate', 'alice_rate'])

# !!!! ==== POVERTY RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!
df['poverty_quartile'] = pd.qcut(df['poverty_rate'], 4, labels=[1, 2, 3, 4])
df['caller_quartile'] = pd.qcut(df['callers_per_1000'], 4, labels=[1, 2, 3, 4])

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
    y = 4 - int(row["caller_quartile"])
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
ax.set_xlabel("Below Alice Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & Below Alice Rate")
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
    4 - df['caller_quartile'].astype(int),  # y = reversed caller quartile
    df['poverty_quartile'].astype(int) - 1  # x = poverty quartile (0-based)
))

# define color matrix
color_matrix = [
    ["#21296B", "#5082F0", "#CCCCCC", "#CCCCCC"],
    ["#5082F0", "#CCCCCC", "#CCCCCC", "#CCCCCC"],
    ["#CCCCCC", "#CCCCCC", "#CCCCCC", "#F47925"],
    ["#CCCCCC", "#CCCCCC", "#F47925", "#D12626"]
]

# map (y, x) to color
color_dict = {(y, x): color_matrix[y][x] for y in range(4) for x in range(4)}
df['bivariate_color'] = df['bivariate_cell'].map(color_dict)

# load and prepare geojson
geojson_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json'
gdf = gpd.read_file(geojson_url)
gdf['zip_code'] = gdf['ZCTA5CE10'].astype(str).str.zfill(5)
gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]
gdf = gdf.merge(df[['zip_code', 'bivariate_color']], on='zip_code', how='left')



# create the plot
fig, ax = plt.subplots(figsize=(11, 11))
gdf.plot(color=gdf['bivariate_color'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)

# create legend parts fresh
legend_labels = [
    "High overrepresentation of callers",
    "Medium overrepresentation of callers",
    "Fair representation of callers",
    "Medium underrepresentation of callers",
    "High underrepresentation of callers"
]

legend_colors = [
    "#21296B", "#5082F0", "#CCCCCC", "#F47925", "#D12626"
]

color_patches = [DrawingArea(20, 10, 0, 0) for _ in legend_colors]
for da, color in zip(color_patches, legend_colors):
    da.add_artist(Rectangle((0, 0), 20, 10, facecolor=color, edgecolor='black'))

left_texts = [TextArea(f"- {label}", textprops={'fontsize': 9}) for label in legend_labels]

legend_items = [HPacker(children=[l, DrawingArea(20, 10, 0, 0), c], align="center", pad=0, sep=10)
                for l, c in zip(left_texts, color_patches)]

right_tags = [
    TextArea("Lower poverty rate w higher call vol", textprops={'fontsize': 10, 'weight': 'bold'}),
    TextArea("Higher poverty rate w lower call vol", textprops={'fontsize': 10, 'weight': 'bold'})
]

right_side = VPacker(
    children=[
        right_tags[0],
        DrawingArea(1, 20, 0, 0),  # vertical spacer
        right_tags[1]
    ],
    align="left", pad=0, sep=60
)

full_legend = HPacker(
    children=[
        VPacker(children=legend_items, align="center", pad=0, sep=4),
        right_side
    ],
    align="center", pad=0, sep=50
)
'''
anchored_box = AnchoredOffsetbox(
    loc='upper left',
    child=full_legend,
    frameon=True,
    pad=0.5,
    bbox_to_anchor=(0.75, 1),  # move it just outside the right side of the plot
    bbox_transform=ax.transAxes
)
ax.add_artist(anchored_box)
'''
ax.set_title("Bexar County Caller Rate vs Poverty Rate by ZIP Code")
ax.axis('off')
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
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

# assign each zip its color
df['bivariate_color_alice'] = df['bivariate_cell_alice'].map(color_dict_alice)

# merge with gdf that now has bivariate_color_alice
gdf = gdf.merge(df[['zip_code', 'bivariate_color_alice']], on='zip_code', how='left')

# remove this line (or comment it out)
# gdf = gdf[gdf['zip_code'].isin(df['zip_code'])]

# define legend components
legend_labels_alice = [
    "High overrepresentation of callers",
    "Medium overrepresentation of callers",
    "Fair representation of callers",
    "Medium underrepresentation of callers",
    "High underrepresentation of callers"
]

legend_colors_alice = [
    "#21296B",  # high overrep
    "#5082F0",  # med overrep
    "#CCCCCC",  # fair
    "#F47925",  # med underrep
    "#D12626"   # high underrep
]

color_patches_alice = [DrawingArea(20, 10, 0, 0) for _ in legend_colors_alice]
for da, color in zip(color_patches_alice, legend_colors_alice):
    da.add_artist(Rectangle((0, 0), 20, 10, facecolor=color, edgecolor='black'))

left_texts_alice = [TextArea(f"- {label}", textprops={'fontsize': 9}) for label in legend_labels_alice]

right_tags_alice = [
    TextArea("Lower ALICE rate w higher call vol", textprops={'fontsize': 10, 'weight': 'bold'}),
    TextArea("Higher ALICE rate w lower call vol", textprops={'fontsize': 10, 'weight': 'bold'})
]

legend_items_alice = [HPacker(children=[l, DrawingArea(20, 10, 0, 0), c], align="center", pad=0, sep=10)
                      for l, c in zip(left_texts_alice, color_patches_alice)]

right_side_alice = VPacker(
    children=[
        right_tags_alice[0],
        DrawingArea(1, 20, 0, 0),  # spacer instead of textarea(" ")
        right_tags_alice[1]
    ],
    align="left", pad=0, sep=60
)

full_legend_alice = HPacker(
    pad=0,
    sep=50,
    align="center",
    children=[VPacker(pad=0, sep=4, align="center", children=legend_items_alice), right_side_alice]
)

# plot
fig, ax = plt.subplots(figsize=(11, 11))  # move this up before add_artist
gdf.plot(color=gdf['bivariate_color_alice'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)
'''
# then add the legend to this ax
anchored_box_alice = AnchoredOffsetbox(
    loc='upper left',
    child=full_legend_alice,
    frameon=True,
    pad=0.5,
    bbox_to_anchor=(0.75, 1),  # move it just outside the right side of the plot
    bbox_transform=ax.transAxes
)
ax.add_artist(anchored_box_alice)
'''
ax.set_title("Bexar County Caller Rate vs ALICE Rate by ZIP Code")
ax.axis('off')
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
plt.show()

'''
NOW WE'RE DOING THE SAME THING BUT WITH POVERTY + ALICE SUM
AND CALLERS PER 1000    
'''
# combine quartile positions into a tuple (y, x) format
df['bivariate_cell_sum'] = list(zip(
    4 - df['caller_quartile'].astype(int),  # y = reversed caller quartile
    df['sum_quartile'].astype(int) - 1      # x = sum quartile (0-based)
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

# assign each zip its color
df['bivariate_color_sum'] = df['bivariate_cell_sum'].map(color_dict_sum)

# merge with gdf that now has bivariate_color_sum
gdf = gdf.merge(df[['zip_code', 'bivariate_color_sum']], on='zip_code', how='left')

# build custom legend for economic instability (poverty + alice)
legend_labels_sum = [
    "High overrepresentation of callers",
    "Medium overrepresentation of callers",
    "Fair representation of callers",
    "Medium underrepresentation of callers",
    "High underrepresentation of callers"
]

legend_colors_sum = [
    "#21296B",  # high overrep
    "#5082F0",  # med overrep
    "#CCCCCC",  # fair
    "#F47925",  # med underrep
    "#D12626"   # high underrep
]

color_patches_sum = [DrawingArea(20, 10, 0, 0) for _ in legend_colors_sum]
for da, color in zip(color_patches_sum, legend_colors_sum):
    da.add_artist(Rectangle((0, 0), 20, 10, facecolor=color, edgecolor='black'))

left_texts_sum = [TextArea(f"- {label}", textprops={'fontsize': 9}) for label in legend_labels_sum]

right_tags_sum = [
    TextArea("Lower economic instability w higher call vol", textprops={'fontsize': 10, 'weight': 'bold'}),
    TextArea("Higher economic instability w lower call vol", textprops={'fontsize': 10, 'weight': 'bold'})
]

legend_items_sum = [HPacker(children=[l, DrawingArea(20, 10, 0, 0), c], align="center", pad=0, sep=10)
                    for l, c in zip(left_texts_sum, color_patches_sum)]

right_side_sum = VPacker(
    children=[
        right_tags_sum[0],
        DrawingArea(1, 20, 0, 0),  # spacer instead of textarea(" ")
        right_tags_sum[1]
    ],
    align="left", pad=0, sep=60
)

full_legend_sum = HPacker(
    pad=0,
    sep=50,
    align="center",
    children=[VPacker(pad=0, sep=4, align="center", children=legend_items_sum), right_side_sum]
)

# plot
fig, ax = plt.subplots(figsize=(11, 11))  # move this up before add_artist
gdf.plot(color=gdf['bivariate_color_sum'].fillna('#E0E0E0'), edgecolor='white', linewidth=0.4, ax=ax)
'''
# then add the legend to this ax
anchored_box_sum = AnchoredOffsetbox(
    loc='upper left',
    child=full_legend_sum,
    frameon=True,
    pad=0.5,
    bbox_to_anchor=(0.75, 1),  # move it just outside the right side of the plot
    bbox_transform=ax.transAxes
)
ax.add_artist(anchored_box_sum)
'''
ax.set_title("Bexar County Caller Rate vs Below ALICE Rate by ZIP Code")
ax.axis('off')
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
plt.show()