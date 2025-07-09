import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# to open virtual environment: venv\Scripts\activate

# load cleaned ZIP-level caller data
df_callers = pd.read_csv('New_211_Client_Cleaned.csv')
df_callers['zip_code'] = df_callers['zip_code'].astype(str).str.zfill(5)

# load ZIP-level demographic indicators
df_demo = pd.read_csv('211 Area Indicators_ZipZCTA.csv')

# keep correct columns from demo data
df_demo = df_demo[['GEO.display_label', 'Pct_Poverty_Households', 'Pct_Below.ALICE_Households']]
df_demo.columns = ['zip_code', 'poverty_rate', 'poverty_alice_sum']

# extract just ZIP codes
df_demo['zip_code'] = df_demo['zip_code'].astype(str).str.extract(r'(\d{5})')

# calculate alice rate = sum - poverty
df_demo['alice_rate'] = df_demo['poverty_alice_sum'] - df_demo['poverty_rate']

# add percent versions for plotting
df_demo['poverty_rate_percent'] = df_demo['poverty_rate']
df_demo['alice_rate_percent'] = df_demo['alice_rate']
df_demo['poverty_alice_sum_percent'] = df_demo['poverty_alice_sum']

# merge with caller data
df = pd.merge(df_callers, df_demo, on='zip_code', how='inner')

# drop missing values
df = df.dropna(subset=['callers_per_1000', 'poverty_rate', 'alice_rate', 'poverty_alice_sum'])

# run Spearman correlations
rho_poverty, pval_poverty = spearmanr(df['callers_per_1000'], df['poverty_rate'])
rho_alice, pval_alice = spearmanr(df['callers_per_1000'], df['alice_rate'])
rho_combo, pval_combo = spearmanr(df['callers_per_1000'], df['poverty_alice_sum'])

# print summary stats
print("\n[Below Alice Stats]")
print(df['poverty_alice_sum'].describe())
print(f"\nMaximum combined poverty + ALICE rate: {df['poverty_alice_sum'].max() * 100:.2f}%")

# convert poverty and alice rates to percent for plotting
df['poverty_rate_percent'] = df['poverty_rate'] * 100
df['alice_rate_percent'] = df['alice_rate'] * 100

# remove zip 78205 before plotting
df_no_78205 = df[df['zip_code'] != '78205'].copy()

# add percent columns for visuals
df_no_78205['poverty_rate_percent'] = df_no_78205['poverty_rate'] * 100
df_no_78205['alice_rate_percent'] = df_no_78205['alice_rate'] * 100
df_no_78205['poverty_alice_sum_percent'] = df_no_78205['poverty_alice_sum'] * 100


'''
VISUALIZATION CODE
'''
# Poverty Rate vs Callers per 1,000

sns.set_style('whitegrid')

plt.figure(figsize=(16, 9))

# plot scatter + trendline
sns.regplot(
    x='poverty_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)

# label all ZIPs
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate_percent'], row['callers_per_1000']),
        xytext=(row['poverty_rate_percent'] + 0.001, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )


# labels & formatting
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()


# ALICE Visuals
plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)


# label all ZIPs
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate_percent'], row['callers_per_1000']),
        xytext=(row['alice_rate_percent'] + 0.001, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )


plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()


# ALICE + Poverty Visuals
# convert to percentage version of sum (e.g. 0.7 → 70%)
df['poverty_alice_sum_percent'] = (df['poverty_rate'] + df['alice_rate']) * 100

# alice + poverty (economic instability) visuals
plt.figure(figsize=(16, 9))

# scatterplot with smoothed line
sns.regplot(
    x='poverty_alice_sum_percent', y='callers_per_1000',
    data=df, lowess=True, truncate=False,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)

# label all zips
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum_percent'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum_percent'] + 0.5, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )

# labels & formatting
plt.title('Spearman: Callers per 1,000 vs. Below Alice', fontsize=16)
plt.xlabel('Below Alice Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()


'''

!!!!! ===== CODE FOR EXCLUDING ZIP 78205 - SPECIFICALLY REQUESTED BY NONPROFIT ===== !!!!!

'''
# remove ZIP 78205 (downtown outlier)
# !!!! ==== POVERTY RATE & CALLER RATE - NO 78205 ==== !!!!

sns.set_style('whitegrid')

plt.figure(figsize=(16, 9))

# plot scatter + trendline
sns.regplot(
    x='poverty_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)

# y limit
plt.ylim(0, 1000)

# label all ZIPs
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate_percent'], row['callers_per_1000']),
        xytext=(row['poverty_rate_percent'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )


# labels & formatting
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE & CALLER RATE - NO 78205 ==== !!!!

plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)

# y limit
plt.ylim(0, 1000)

# label all ZIPs
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate_percent'], row['callers_per_1000']),
        xytext=(row['alice_rate_percent'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )

plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE & POVERTY SUM & CALLER RATE - NO 78205 ==== !!!!

# economic instability vs caller rate (excluding 78205)
plt.figure(figsize=(16, 9))

# scatterplot with smoothed line
sns.regplot(
    x='poverty_alice_sum_percent', y='callers_per_1000',
    data=df_no_78205, lowess=True, truncate=False,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)
# y limit
plt.ylim(0, 1000)
# label all zips
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum_percent'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum_percent'] + 0.5, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )


# labels and limits
plt.title('Spearman: Callers per 1,000 vs. Below Alice', fontsize=16)
plt.xlabel('Below Alice Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

'''

!!!!!! ====== NONPROFIT REQUESTED ZOOMED IN SPEARMEN VISUALS - EXCLUDING OUTLIER ====== !!!!!!

'''
df = df[df['zip_code'] != '78205']

# !!!! ==== POVERTY RATE & CALLER RATE - NO 78205 ==== !!!!

sns.set_style('whitegrid')

plt.figure(figsize=(16, 9))
sns.regplot(
    x='poverty_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)
plt.ylim(0, 400)            # ADDED CHANGE IN CODE FOR VISUAL
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate_percent'], row['callers_per_1000']),
        xytext=(row['poverty_rate_percent'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE & CALLER RATE - NO 78205 ==== !!!!

plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate_percent', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)
plt.ylim(0, 400)            # ADDED CHANGE IN CODE FOR VISUAL
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate_percent'], row['callers_per_1000']),
        xytext=(row['alice_rate_percent'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )
plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE & POVERTY SUM & CALLER RATE - NO 78205 ==== !!!!

# economic instability vs caller rate (excluding 78205)
plt.figure(figsize=(16, 9))

# scatterplot with smoothed trendline
sns.regplot(
    x='poverty_alice_sum_percent', y='callers_per_1000',
    data=df_no_78205, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)

# set y limit to better visualize distribution
plt.ylim(0, 400)

# label all zips
for _, row in df_no_78205.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum_percent'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum_percent'] + 0.5, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )

# labels and axis formatting
plt.title('Spearman: Callers per 1,000 vs. Below Alice', fontsize=16)
plt.xlabel('Below Alice Rate (%)', fontsize=12)
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.show()


# CODE TO CREATE SPEARMEN CSV
spearman_results = {
    'Metric': ['Poverty Rate', 'ALICE Rate', 'Below Alice'],
    'Spearman ρ': [rho_poverty, rho_alice, rho_combo],
    'p-value': [pval_poverty, pval_alice, pval_combo]
}
df_spearman = pd.DataFrame(spearman_results)
df_spearman.to_csv('211_Spearman_Correlation_Results.csv', index=False)

# save merged df to CSV for future reference
df.to_csv('211_Merged_ZIP_Economic_Instability.csv', index=False)
print("[Merged data saved to '211_Merged_ZIP_Economic_Instability.csv']")

# save cleaned demographic data to CSV for future reference
df_demo = df_demo.dropna()
df_demo.to_csv('211_Demographic_Data_Cleaned.csv', index=False)
print("[Merged data saved to '211_Demographic_Data_Cleaned.csv']")