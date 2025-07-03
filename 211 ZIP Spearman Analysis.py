import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
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

# add correct combo metric (sum, not average)
df['poverty_alice_sum'] = df['poverty_rate'] + df['alice_rate']

# run Spearman correlations
rho_poverty, pval_poverty = spearmanr(df['callers_per_1000'], df['poverty_rate'])
rho_alice, pval_alice = spearmanr(df['callers_per_1000'], df['alice_rate'])
rho_combo, pval_combo = spearmanr(df['callers_per_1000'], df['poverty_alice_sum'])

print("\n[Spearman Correlation Results]")
print(f"Callers per 1,000 vs. Poverty Rate:        ρ = {rho_poverty:.3f}, p = {pval_poverty:.4f}")
print(f"Callers per 1,000 vs. ALICE Rate:          ρ = {rho_alice:.3f}, p = {pval_alice:.4f}")
print(f"Callers per 1,000 vs. Poverty+ALICE Sum:   ρ = {rho_combo:.3f}, p = {pval_combo:.4f}")

'''
VISUALIZATION CODE
'''
# Poverty Rate vs Callers per 1,000

sns.set_style('whitegrid')

plt.figure(figsize=(16, 9))

# plot scatter + trendline
sns.regplot(
    x='poverty_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)

# label all ZIPs
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate'], row['callers_per_1000']),
        xytext=(row['poverty_rate'] + 0.001, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )


# labels & formatting
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()
plt.show()


# ALICE Visuals
plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)


# label all ZIPs
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate'], row['callers_per_1000']),
        xytext=(row['alice_rate'] + 0.001, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )


plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.show()


# ALICE + Poverty Visuals
plt.figure(figsize=(16, 9))
sns.regplot(
    x='poverty_alice_sum', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)

# label all ZIPs
for _, row in df.iterrows():
    offset = 15 if row['zip_code'] == '78205' else 5
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum'] + 0.001, row['callers_per_1000'] + offset),
        fontsize=7,
        color='black',
        alpha=0.7
    )


plt.title('Spearman: Callers per 1,000 vs. Economic Instability', fontsize=16)
plt.xlabel('Sum of Poverty + ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.show()


'''

!!!!! ===== CODE FOR EXCLUDING ZIP 78205 - SPECIFICALLY REQUESTED BY NONPROFIT ===== !!!!!

'''
# remove ZIP 78205 (downtown outlier)
df = df[df['zip_code'] != '78205']

# !!!! ==== POVERTY RATE & CALLER RATE - NO 78205 ==== !!!!

sns.set_style('whitegrid')

plt.figure(figsize=(16, 9))

# plot scatter + trendline
sns.regplot(
    x='poverty_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)

# y limit
plt.ylim(0, 1000)

# label all ZIPs
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate'], row['callers_per_1000']),
        xytext=(row['poverty_rate'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )


# labels & formatting
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE & CALLER RATE - NO 78205 ==== !!!!

plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)

# y limit
plt.ylim(0, 1000)

# label all ZIPs
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate'], row['callers_per_1000']),
        xytext=(row['alice_rate'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )

plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE & POVERTY SUM & CALLER RATE - NO 78205 ==== !!!!
plt.figure(figsize=(16, 9))
sns.regplot(
    x='poverty_alice_sum', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)

# y limit
plt.ylim(0, 1000)

# label all ZIPs
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum'] + 0.01, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )

plt.title('Spearman: Callers per 1,000 vs. Economic Instability', fontsize=16)
plt.xlabel('Sum of Poverty + ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
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
    x='poverty_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'}
)
plt.ylim(0, 400)            # ADDED CHANGE IN CODE FOR VISUAL
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_rate'], row['callers_per_1000']),
        xytext=(row['poverty_rate'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )
plt.title('Spearman: Callers per 1,000 vs. Poverty Rate', fontsize=16)
plt.xlabel('Poverty Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE RATE & CALLER RATE - NO 78205 ==== !!!!

plt.figure(figsize=(16, 9))
sns.regplot(
    x='alice_rate', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'orange'}
)
plt.ylim(0, 400)            # ADDED CHANGE IN CODE FOR VISUAL
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['alice_rate'], row['callers_per_1000']),
        xytext=(row['alice_rate'] + 0.001, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )
plt.title('Spearman: Callers per 1,000 vs. ALICE Rate', fontsize=16)
plt.xlabel('ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.show()

# !!!! ==== ALICE & POVERTY SUM & CALLER RATE - NO 78205 ==== !!!!

plt.figure(figsize=(16, 9))
sns.regplot(
    x='poverty_alice_sum', y='callers_per_1000',
    data=df, lowess=True,
    scatter_kws={'alpha': 0.6}, line_kws={'color': 'purple'}
)
plt.ylim(0, 400)            # ADDED CHANGE IN CODE FOR VISUAL
# label all ZIPs
for _, row in df.iterrows():
    plt.annotate(
        row['zip_code'],
        xy=(row['poverty_alice_sum'], row['callers_per_1000']),
        xytext=(row['poverty_alice_sum'] + 0.01, row['callers_per_1000'] + 5),
        fontsize=7,
        color='black',
        alpha=0.7
    )
plt.title('Spearman: Callers per 1,000 vs. Economic Instability', fontsize=16)
plt.xlabel('Sum of Poverty + ALICE Rate (%)', fontsize=12)
plt.ylabel('Callers per 1,000 Residents', fontsize=12)
plt.tight_layout()
plt.show()

# CODE TO CREATE SPEARMEN CSV
spearman_results = {
    'Metric': ['Poverty Rate', 'ALICE Rate', 'Economic Instability'],
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