import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import AnchoredText
'''
This script performs cross-tabulation analysis between LISA results for economic need (poverty) and demand (caller rate).
It generates a 4x4 matrix showing the relationship between local spatial autocorrelation in poverty rates
and caller rates across ZIP codes.
The output is saved as a CSV file for further analysis.
Technically it's a 5x5 matrix since we include 'NS' (not significant) as a fifth category.
This is useful for understanding how areas with high/low poverty rates correlate with areas that have high/low demand for 2-1-1 services.
It helps identify patterns of need and demand that can inform resource allocation and service delivery strategies.
'''


# load LISA results
df_callers = pd.read_csv("final_efficient_chosen_tests/LISA_CallerRate_Results.csv")
df_poverty = pd.read_csv("final_efficient_chosen_tests/BEXAR_LISA_Poverty_Results.csv")

# merge both on ZIP
df = pd.merge(df_callers, df_poverty, on='zip_code', how='inner')

# build 5x5 matrix (the 5th row/column is for 'NS' - not significant)
matrix = pd.crosstab(
    df['lisa_poverty_quad_label'],  # rows: economic need
    df['lisa_callers_quad_label'],  # cols: demand
    rownames=['Poverty LISA'],
    colnames=['Caller Rate LISA']
)

print(matrix)
matrix.to_csv("final_efficient_chosen_tests/BEXAR_CrossTab_Caller_vs_Poverty.csv")
print("Cross-tab matrix saved as 'BEXAR_CrossTab_Caller_vs_Poverty.csv'")

'''
The following is the visualization code for the cross-tab matrix.
This part is optional and can be used to create a heatmap of the cross-tab results.
'''

# load your matrix
matrix = pd.read_csv("final_efficient_chosen_tests/BEXAR_CrossTab_Caller_vs_Poverty.csv", index_col=0)

# order of labels
labels = ['HH', 'LH', 'HL', 'LL', 'NS']
matrix = matrix.reindex(index=labels, columns=labels)

# define cell fill
blue_cells = [('LH', 'HH'), ('LH', 'HL'), ('LL', 'HH'), ('LL', 'HL')]
red_cells   = [('HH', 'LH'), ('HH', 'LL'), ('HL', 'LH'), ('HL', 'LL')]

# set up plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.invert_yaxis()

for y, row_label in enumerate(labels):
    for x, col_label in enumerate(labels):
        count = matrix.loc[row_label, col_label] if pd.notna(matrix.loc[row_label, col_label]) else 0

        # fill color
        if row_label == 'NS' or col_label == 'NS':
            facecolor = '#FFFFFF'     # white
            text_color = 'black'
        elif (row_label, col_label) in blue_cells:
            facecolor = '#21296B'     # COLD SPOTS
            text_color = 'white'
        elif (row_label, col_label) in red_cells:
            facecolor = '#D12626'     # HOT SPOTS
            text_color = 'white'
        else:
            facecolor = '#E0E0E0'     # gray
            text_color = 'black'

        # draw cell
        ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=facecolor, edgecolor='black', linewidth=1))

        # draw count with text color
        ax.text(
            x + 0.5, y + 0.5,
            str(int(count)),
            va='center', ha='center',
            fontsize=12,
            color=text_color,
            fontweight='bold'
        )


# axes labels
ax.set_xticks([i + 0.5 for i in range(5)])
ax.set_xticklabels(labels)
ax.set_yticks([i + 0.5 for i in range(5)])
ax.set_yticklabels(labels)
ax.set_xlabel("Caller Rate LISA")
ax.set_ylabel("Poverty Rate LISA")
ax.set_title("Bexar Caller Rate vs Poverty LISA Alignment Matrix", fontsize=14)

# grid lines
ax.set_xticks(range(6), minor=True)
ax.set_yticks(range(6), minor=True)
ax.grid(which='minor', color='black', linewidth=1)

plt.tight_layout()
plt.show()

'''
Now lets do the same for Below ALICE LISA
This will create a similar cross-tabulation matrix for Below ALICE rates.
'''

df_alice = pd.read_csv("final_efficient_chosen_tests/BEXAR_LISA_Below_ALICE_Results.csv")
# merge on ZIP
df = pd.merge(df_callers, df_alice, on='zip_code', how='inner')

# create 5x5 matrix
labels = ['HH', 'LH', 'HL', 'LL', 'NS']
matrix = pd.crosstab(
    df['lisa_alice_quad_label'],  # rows
    df['lisa_callers_quad_label'],  # columns
    rownames=['Below ALICE LISA'],
    colnames=['Caller Rate LISA']
)

print(matrix)
matrix.to_csv("final_efficient_chosen_tests/BEXAR_CrossTab_Caller_vs_Below_ALICE.csv")
print("Cross-tab matrix saved as 'BEXAR_CrossTab_Caller_vs_Below_ALICE.csv'")


# force full grid in case a label is missing
matrix = matrix.reindex(index=labels, columns=labels, fill_value=0)

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.invert_yaxis()

for y, row_label in enumerate(labels):
    for x, col_label in enumerate(labels):
        count = matrix.loc[row_label, col_label]

        # fill + text color
        if row_label == 'NS' or col_label == 'NS':
            facecolor = '#FFFFFF'
            text_color = 'black'
        elif (row_label, col_label) in blue_cells:
            facecolor = '#21296B'
            text_color = 'white'
        elif (row_label, col_label) in red_cells:
            facecolor = '#D12626'
            text_color = 'white'
        else:
            facecolor = '#E0E0E0'
            text_color = 'black'

        # draw box
        ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=facecolor, edgecolor='black', linewidth=1))

        # draw count
        ax.text(
            x + 0.5, y + 0.5,
            str(int(count)),
            va='center', ha='center',
            fontsize=12,
            color=text_color,
            fontweight='bold'
        )

# labels
ax.set_xticks([i + 0.5 for i in range(5)])
ax.set_xticklabels(labels)
ax.set_yticks([i + 0.5 for i in range(5)])
ax.set_yticklabels(labels)
ax.set_xlabel("Caller Rate LISA")
ax.set_ylabel("Below ALICE LISA")
ax.set_title("Bexar Caller Rate vs Below ALICE LISA Alignment Matrix", fontsize=14)

# grid
ax.set_xticks(range(6), minor=True)
ax.set_yticks(range(6), minor=True)
ax.grid(which='minor', color='black', linewidth=1)

plt.tight_layout()
plt.show()

'''
Now lets throw all this onto a map
This will visualize the cross-tab results on a map of Texas ZIP codes.
'''
# load ZIP shapefile
gdf_shape = gpd.read_file("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-geojson/master/tx_texas_zip_codes_geo.min.json")
gdf_shape['zip_code'] = gdf_shape['ZCTA5CE10'].astype(str).str.zfill(5)

# merge in LISA results (for Below ALICE map)
df = pd.merge(df_callers[['zip_code', 'lisa_callers_quad_label']],
              df_alice[['zip_code', 'lisa_alice_quad_label']],
              on='zip_code', how='inner')

# merge
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)
gdf_shape['zip_code'] = gdf_shape['zip_code'].astype(str).str.zfill(5)

gdf = gdf_shape.merge(df, on='zip_code', how='inner')

# create combo label
gdf['combo'] = list(zip(gdf['lisa_alice_quad_label'], gdf['lisa_callers_quad_label']))

# define combo color logic
blue_cells = [('LH', 'HH'), ('LH', 'HL'), ('LL', 'HH'), ('LL', 'HL')]
red_cells   = [('HH', 'LH'), ('HH', 'LL'), ('HL', 'LH'), ('HL', 'LL')]
ns_cells     = [('NS', x) for x in labels] + [(x, 'NS') for x in labels]

def assign_color(combo):
    if combo in blue_cells:
        return '#21296B'  # blue
    elif combo in red_cells:
        return '#D12626'  # red
    elif combo in ns_cells:
        return '#FFFFFF'  # not significant
    else:
        return '#CCCCCC'  # aligned/neutral

# create combo label
gdf['combo'] = list(zip(gdf['lisa_alice_quad_label'], gdf['lisa_callers_quad_label']))

# define combo color logic
blue_cells = [('LH', 'HH'), ('LH', 'HL'), ('LL', 'HH'), ('LL', 'HL')]
red_cells   = [('HH', 'LH'), ('HH', 'LL'), ('HL', 'LH'), ('HL', 'LL')]
ns_cells     = [('NS', x) for x in labels] + [(x, 'NS') for x in labels]

def assign_color(combo):
    if combo in blue_cells:
        return '#21296B'  # blue
    elif combo in red_cells:
        return '#D12626'  # red
    elif combo in ns_cells:
        return '#FFFFFF'  # not significant
    else:
        return '#CCCCCC'  # aligned/neutral

gdf['color'] = gdf['combo'].apply(assign_color)


# filter ZIPs with red or blue color
labeled_zips = gdf[gdf['color'].isin(['#21296B', '#D12626'])]

# plot map
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, color="#F5F5F5", edgecolor='lightgray')  # base
gdf.plot(ax=ax, color=gdf['color'], edgecolor='black', linewidth=0.3)

# ZIP code labels on red/blue only
'''
for idx, row in labeled_zips.iterrows():
    ax.annotate(
        text=row['zip_code'],
        xy=(row.geometry.centroid.x, row.geometry.centroid.y),
        fontsize=8,
        color='white',
        ha='center',
        va='center'
    )
'''
# only label ZIP 78861 for now
zip_to_label = '78861'
if zip_to_label in gdf['zip_code'].values:
    row = gdf[gdf['zip_code'] == zip_to_label].iloc[0]
    ax.annotate(
        text=zip_to_label,
        xy=(row.geometry.centroid.x, row.geometry.centroid.y),
        fontsize=8,
        color='white',
        ha='center',
        va='center'
    )

# legend
legend_elements = [
    mpatches.Patch(color='#21296B', label='High Calls + Low Need (Misalignment)'),
    mpatches.Patch(color='#D12626', label='Low Calls + High Need (Underserved)'),
    mpatches.Patch(color='#CCCCCC', label='Aligned (HH/LL)'),
    mpatches.Patch(color='#FFFFFF', label='Not Statistically Significant')
]

ax.legend(handles=legend_elements, title="Need vs Demand", loc='upper right')
ax.set_title("ZIP-level Map: Caller Rate vs Below ALICE LISA Quadrants", fontsize=15)
ax.axis('off')

# extract ZIPs into string lists grouped by type
red_zips = labeled_zips[labeled_zips['color'] == '#D12626']['zip_code'].tolist()
blue_zips = labeled_zips[labeled_zips['color'] == '#21296B']['zip_code'].tolist()
print("Red ZIPs:", red_zips)
print("Blue ZIPs:", blue_zips)
print("Total red:", len(red_zips), "Total blue:", len(blue_zips))
# Build ZIP text for display
zip_legend_text = (
    "Underserved ZIPs:\n" + ', '.join(red_zips) + "\n\n" +
    "Misaligned ZIPs:\n" + ', '.join(blue_zips)
)

# Add as anchored textbox on the side
at = AnchoredText(zip_legend_text,
                  prop=dict(size=9), frameon=True,
                  loc='lower left',  # adjust as needed
                  bbox_to_anchor=(1.05, 0), bbox_transform=ax.transAxes,
                  borderpad=0.5)
ax.add_artist(at)
plt.tight_layout()
plt.show()
