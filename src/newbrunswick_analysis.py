import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/NewBrunswick")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")
prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")


# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Ensure numeric columns are numeric
for col in ["Total Emissions (tonnes CO2e)"]:
    if col in emission_df.columns:
        emission_df[col] = pd.to_numeric(emission_df[col], errors="coerce")

# ===================================================
# Part 1 — Segmentation & Trend (NB totals per year)
# ===================================================
new_brunswick_emission = emission_df[emission_df['Facility Province'] == 'New Brunswick'].copy()

grouped_new_brunswick_emission = (
    new_brunswick_emission
    .groupby('Reference Year')[['Total Emissions (tonnes CO2e)']]
    .sum()
    .reset_index()
    .rename(columns={'Total Emissions (tonnes CO2e)': 'New Brunswick Total Emission (tonnes CO2e)'})
)
grouped_new_brunswick_emission['New Brunswick Total Emission (tonnes CO2e)'] = (
    grouped_new_brunswick_emission['New Brunswick Total Emission (tonnes CO2e)'].round(2)
)

nb_totals_csv = os.path.join(OUT_DIR, "nb_total_emissions_by_year.csv")
grouped_new_brunswick_emission.to_csv(nb_totals_csv, index=False)
print(f"Saved NB totals by year → {nb_totals_csv}")

# ---- Targets slice ----
new_brunswick_target = provincial_targets_df[provincial_targets_df['Province'] == 'New Brunswick'].reset_index(drop=True)
nb_targets_csv = os.path.join(OUT_DIR, "nb_targets_table.csv")
new_brunswick_target.to_csv(nb_targets_csv, index=False)
print(f"Saved NB targets table → {nb_targets_csv}")

# Baseline (1990) – compute if present
can_plot_targets = True
if (grouped_new_brunswick_emission['Reference Year'] == 1990).any() and \
   ('Reduction Upper Bound' in new_brunswick_target.columns) and \
   len(new_brunswick_target) >= 2:
    new_brunswick_reference_total_emission = (
        grouped_new_brunswick_emission.loc[
            grouped_new_brunswick_emission['Reference Year'] == 1990,
            'New Brunswick Total Emission (tonnes CO2e)'
        ].round(2).values[0]
    )

    # Annualized reduction rates from your table (keep your indexing)
    new_brunswick_baseline_annual_target_reduction_2030 = int(new_brunswick_target['Reduction Upper Bound'][0]) / 35
    new_brunswick_baseline_annual_target_reduction_2050 = round(int(new_brunswick_target['Reduction Upper Bound'][1]) / 45, 2)

    # Build axes and target arrays (follow your loop structure)
    x_target_axis = np.array([x for x in grouped_new_brunswick_emission['Reference Year']])
    y_target_axis_2030 = grouped_new_brunswick_emission['New Brunswick Total Emission (tonnes CO2e)'].copy().to_numpy()
    y_target_axis_2050 = grouped_new_brunswick_emission['New Brunswick Total Emission (tonnes CO2e)'].copy().to_numpy()

    reduction_factor_2030 = 1 - (new_brunswick_baseline_annual_target_reduction_2030 / 100)
    reduction_factor_2050 = 1 - (new_brunswick_baseline_annual_target_reduction_2050 / 100)

    # Apply annual reduction factors (keep your indexing pattern)
    for i in range(2, len(y_target_axis_2030)):
        y_target_axis_2030[i] = y_target_axis_2030[i-1] * reduction_factor_2030
    for i in range(2, len(y_target_axis_2050)):
        y_target_axis_2050[i] = y_target_axis_2050[i-1] * reduction_factor_2050
else:
    print("⚠️ Could not compute NB target lines (1990 baseline or target columns/rows missing).")
    can_plot_targets = False

# ---- Plot: Actual vs Targets (in Mt) ----
y_axis_million = np.array(grouped_new_brunswick_emission['New Brunswick Total Emission (tonnes CO2e)'] / 1e6)
x_axis = np.array(grouped_new_brunswick_emission['Reference Year'])

plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis_million, color='blue', marker='o', label='Actual Emission')

if can_plot_targets:
    plt.plot(x_axis, y_target_axis_2030 / 1e6, color='green', linestyle='--', label='Target 2030')
    plt.plot(x_axis, y_target_axis_2050 / 1e6, color='red', linestyle='--', label='Target 2050')

for i, value in enumerate(y_axis_million):
    plt.text(x_axis[i], value, f'{value:.2f}', ha='right')

plt.grid(True)
plt.xticks(x_axis)
plt.title('New Brunswick Total Emission (Megatonnes (Mt CO₂e)) / Year')
plt.legend()
plt.tight_layout()
nb_trend_png = os.path.join(OUT_DIR, "nb_total_emissions_trend_actual_vs_targets.png")
plt.savefig(nb_trend_png, dpi=200)
plt.show()
print(f"Saved NB trend plot → {nb_trend_png}")

# ======================
# Part 2 — Sector split
# ======================
grouped_new_brunswick_facility = (
    new_brunswick_emission
    .groupby(['Reference Year', 'Facility Description'])['Total Emissions (tonnes CO2e)']
    .sum()
    .reset_index()
    .rename(columns={'Total Emissions (tonnes CO2e)': 'Total Facility Emission (tonnes CO2e)'})
)
grouped_new_brunswick_facility['Total Facility Emission (tonnes CO2e)'] = (
    grouped_new_brunswick_facility['Total Facility Emission (tonnes CO2e)'].round(2)
)

nb_facility_csv = os.path.join(OUT_DIR, "nb_facility_emissions_by_year.csv")
grouped_new_brunswick_facility.to_csv(nb_facility_csv, index=False)
print(f"Saved NB facility-by-year table → {nb_facility_csv}")

# Top 10 facilities by total emissions across all years
facility_sums = grouped_new_brunswick_facility.groupby('Facility Description')['Total Facility Emission (tonnes CO2e)'].sum()
top_10_facilities = facility_sums.sort_values(ascending=False).head(10).index

df_top10 = grouped_new_brunswick_facility[
    grouped_new_brunswick_facility['Facility Description'].isin(top_10_facilities)
].copy()

emission_pivot = df_top10.pivot(
    index='Facility Description',
    columns='Reference Year',
    values='Total Facility Emission (tonnes CO2e)'
).fillna(0)

plt.figure(figsize=(12, 6))
ax = sns.heatmap(
    emission_pivot / 1e6,  # Mt
    cmap='RdYlGn_r',
    linecolor='white',
    linewidths=0.5,
    cbar_kws={'label': 'CO2e Emission (Megatonnes (Mt CO₂e))'},
    annot=False,
    fmt='.2f'
)
plt.xticks(rotation=90)
plt.title('New Brunswick Top 10 GHG Emission Facilities')
plt.xlabel('Reference Year')
plt.ylabel('Facility Description')
plt.tight_layout()
nb_heatmap_png = os.path.join(OUT_DIR, "nb_top10_facilities_heatmap.png")
plt.savefig(nb_heatmap_png, dpi=200)
plt.show()
print(f"Saved NB heatmap → {nb_heatmap_png}")
