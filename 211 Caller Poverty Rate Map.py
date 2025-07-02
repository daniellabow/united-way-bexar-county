import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

# to open virtual environment: venv\Scripts\activate

# load cleaned ZIP-level caller data
df_callers = pd.read_csv('Filtered_Num_Clients_By_ZIP.csv')
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
df['poverty_quantile'] = pd.qcut(df['poverty_rate'], 5, labels=[1, 2, 3, 4, 5])
df['caller_rate_quantile'] = pd.qcut(df['callers_per_1000'], 5, labels=[1, 2, 3, 4, 5])

color_matrix = [
    ["#08306b", "#08519c", "#6baed6", "#ffffff", "#ffffff"],  # Call Rate Q5 (top)
    ["#2171b5", "#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000", "#f16913"],
    ["#ffffff", "#ffffff", "#ffd000", "#f16913", "#99000d"],  # Call Rate Q1 (bottom)
]

# empty 5x5 count grid
count_grid = np.zeros((5, 5), dtype=int)

# popcounts from merged df
for _, row in df.iterrows():
    x = int(row["poverty_quantile"]) - 1  # column
    y = 5 - int(row["caller_rate_quantile"])  # row (reverse for display)
    count_grid[y, x] += 1

fig, ax = plt.subplots(figsize=(8, 6))

# grid w/ assigned fixed bivariate color matrix
for y in range(5):
    for x in range(5):
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = count_grid[y, x]
        if count > 0:
            ax.text(
                x + 0.5, y + 0.5, str(count),
                va='center', ha='center',
                color='black',
                fontsize=10
            )
        else:
            ax.text(
                x + 0.5, y + 0.5, str("0"),
                va='center', ha='center',
                color='black',
                fontsize=10
            )

ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_xticks(np.arange(5) + 0.5)
ax.set_yticks(np.arange(5) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4', '5'])
ax.set_yticklabels(['5', '4', '3', '2', '1'])  # Top to bottom
ax.set_xlabel("Poverty Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & Poverty Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!
df["alice_quantile"] = pd.qcut(df["alice_rate"], 5, labels=[1, 2, 3, 4, 5])
df["caller_quantile"] = pd.qcut(df["callers_per_1000"], 5, labels=[1, 2, 3, 4, 5])

alice_grid = np.zeros((5, 5), dtype=int)

for _, row in df.iterrows():
    x = int(row["alice_quantile"]) - 1
    y = 5 - int(row["caller_quantile"])  # reverse Y so 1 is bottom
    alice_grid[y, x] += 1

df["sum_quantile"] = pd.qcut(df["poverty_alice_sum"], 5, labels=[1, 2, 3, 4, 5])
color_matrix_alice = [
    ["#08306b", "#08519c", "#6baed6", "#ffffff", "#ffffff"],
    ["#2171b5", "#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000", "#f16913"],
    ["#ffffff", "#ffffff", "#ffd000", "#f16913", "#99000d"],
]

fig, ax = plt.subplots(figsize=(8, 6))

# grid w/ assigned fixed bivariate color matrix
for y in range(5):
    for x in range(5):
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = alice_grid[y, x]
        if count > 0:
            ax.text(
                x + 0.5, y + 0.5, str(count),
                va='center', ha='center',
                color='black',
                fontsize=10
            )
        else:
            ax.text(
                x + 0.5, y + 0.5, str("0"),
                va='center', ha='center',
                color='black',
                fontsize=10
            )

ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_xticks(np.arange(5) + 0.5)
ax.set_yticks(np.arange(5) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4', '5'])
ax.set_yticklabels(['5', '4', '3', '2', '1'])  # Top to bottom
ax.set_xlabel("ALICE Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & ALICE Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()


# !!!! ==== POVERTY + ALICE SUM vs CALLERS PER 1000 HEAT MAP ==== !!!!
df["sum_quantile"] = pd.qcut(df["poverty_alice_sum"], 5, labels=[1, 2, 3, 4, 5])
df["caller_quantile"] = pd.qcut(df["callers_per_1000"], 5, labels=[1, 2, 3, 4, 5])

sum_grid = np.zeros((5, 5), dtype=int)

for _, row in df.iterrows():
    x = int(row["sum_quantile"]) - 1
    y = 5 - int(row["caller_quantile"])
    sum_grid[y, x] += 1

df["sum_quantile"] = pd.qcut(df["poverty_alice_sum"], 5, labels=[1, 2, 3, 4, 5])
color_matrix_alice = [
    ["#08306b", "#08519c", "#6baed6", "#ffffff", "#ffffff"],
    ["#2171b5", "#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000", "#f16913"],
    ["#ffffff", "#ffffff", "#ffd000", "#f16913", "#99000d"],
]

fig, ax = plt.subplots(figsize=(8, 6))

# grid w/ assigned fixed bivariate color matrix
for y in range(5):
    for x in range(5):
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = sum_grid[y, x]
        if count > 0:
            ax.text(
                x + 0.5, y + 0.5, str(count),
                va='center', ha='center',
                color='black',
                fontsize=10
            )
        else:
            ax.text(
                x + 0.5, y + 0.5, str("0"),
                va='center', ha='center',
                color='black',
                fontsize=10
            )

ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_xticks(np.arange(5) + 0.5)
ax.set_yticks(np.arange(5) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4', '5'])
ax.set_yticklabels(['5', '4', '3', '2', '1'])  # Top to bottom
ax.set_xlabel("ALICE Poverty Sum")
ax.set_ylabel("Caller Rate")
ax.set_title("ZIP Count by Caller Rate & ALICE + Poverty Sum")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()