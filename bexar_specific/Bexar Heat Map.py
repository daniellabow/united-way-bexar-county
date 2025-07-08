import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

# to open virtual environment: venv\Scripts\activate

# load cleaned ZIP-level caller data
df = pd.read_csv('bexar_specific/Bexar_County_ZIP_Eco_Indicator_Data.csv')
df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)

# add correct combo for sum, not avg
df['poverty_alice_sum'] = df['poverty_rate'] + df['alice_rate']

# !!!! ==== POVERTY RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!
df['poverty_quartile'] = pd.qcut(df['poverty_rate'], 4, labels=[1, 2, 3, 4])
df['caller_rate_quartile'] = pd.qcut(df['callers_per_1000'], 4, labels=[1, 2, 3, 4])

color_matrix = [
    ["#08306b", "#6baed6", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffd000", "#99000d"]
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
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = count_grid[y, x]
        ax.text(x + 0.5, y + 0.5, str(count), ha='center', va='center', fontsize=10)

ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.set_xticks(np.arange(4) + 0.5)
ax.set_yticks(np.arange(4) + 0.5)
ax.set_xticklabels(['1', '2', '3', '4'])
ax.set_yticklabels(['4', '3', '2', '1'])
ax.set_xlabel("Poverty Rate")
ax.set_ylabel("Caller Rate")
ax.set_title("Bexar County ZIP Count by Caller Rate & Poverty Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE vs CALLERS PER 1000 HEAT MAP ==== !!!!
# Assign quantiles
df["alice_quartile"] = pd.qcut(df["alice_rate"], 4, labels=[1, 2, 3, 4])
df["caller_quartile"] = pd.qcut(df["callers_per_1000"], 4, labels=[1, 2, 3, 4])

# Create a 4x4 grid
alice_grid = np.zeros((4, 4), dtype=int)

# Fill grid (Y reversed to make quantile 1 on bottom)
for _, row in df.iterrows():
    x = int(row["alice_quartile"]) - 1
    y = 4 - int(row["caller_quartile"])  # 4 - since we're in a 4x4 grid
    alice_grid[y, x] += 1

# New 4x4 color matrix
color_matrix_alice = [
    ["#08306b", "#6baed6", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffd000", "#99000d"]
]

# Plot heatmap
fig, ax = plt.subplots(figsize=(7, 6))

for y in range(4):
    for x in range(4):
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix_alice[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = alice_grid[y, x]
        ax.text(
            x + 0.5, y + 0.5, str(count),
            va='center', ha='center',
            color='black',
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
ax.set_title("Bexar County ZIP Count by Caller Rate & ALICE Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()

# !!!! ==== POVERTY + ALICE SUM vs CALLERS PER 1000 HEAT MAP ==== !!!!
df["sum_quartile"] = pd.qcut(df["poverty_alice_sum"], 4, labels=[1, 2, 3, 4])
df["caller_quartile"] = pd.qcut(df["callers_per_1000"], 4, labels=[1, 2, 3, 4])

# Create 4x4 grid
sum_grid = np.zeros((4, 4), dtype=int)

# Populate grid
for _, row in df.iterrows():
    x = int(row["sum_quartile"]) - 1
    y = 4 - int(row["caller_quartile"])  # reverse Y for top-bottom
    sum_grid[y, x] += 1

# New 4x4 color matrix
color_matrix_sum = [
    ["#08306b", "#6baed6", "#ffffff", "#ffffff"],
    ["#6baed6", "#ffffff", "#ffffff", "#ffffff"],
    ["#ffffff", "#ffffff", "#ffffff", "#ffd000"],
    ["#ffffff", "#ffffff", "#ffd000", "#99000d"]
]

# Plot
fig, ax = plt.subplots(figsize=(7, 6))

for y in range(4):
    for x in range(4):
        ax.add_patch(plt.Rectangle(
            (x, y), 1, 1,
            facecolor=color_matrix_sum[y][x],
            edgecolor='black',
            linewidth=1
        ))
        count = sum_grid[y, x]
        ax.text(
            x + 0.5, y + 0.5, str(count),
            va='center', ha='center',
            color='black',
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
ax.set_title("Bexar County ZIP Count by Caller Rate & Economic Instability Rate")
ax.invert_yaxis()
ax.set_aspect('equal')
plt.grid(False)
plt.tight_layout()
plt.show()