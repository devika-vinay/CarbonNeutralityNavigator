import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Paths that work from ANY working directory ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))          # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/BritishColumbia")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")

# --- Load emissions ---
emission_df = pd.read_csv(emissions_csv)

# =========================
# Part 1: BC totals by year
# =========================
bc_emission = emission_df[emission_df['Facility Province'] == 'British Columbia']
grouped_bc_emission = (
    bc_emission
    .groupby('Reference Year')[['Total Emissions (tonnes CO2e)']]
    .sum()
    .reset_index()
    .rename(columns={'Total Emissions (tonnes CO2e)': 'BC Total Emission (tonnes CO2e)'})
)
grouped_bc_emission['BC Total Emission (tonnes CO2e)'] = (
    grouped_bc_emission['BC Total Emission (tonnes CO2e)'].round(2)
)

# Save the table too
grouped_bc_emission.to_csv(os.path.join(OUT_DIR, "bc_total_by_year.csv"), index=False)

# --- Plot: BC totals (label in million tonnes) ---
x_axis = np.array(grouped_bc_emission['Reference Year'])
y_axis = np.array(grouped_bc_emission['BC Total Emission (tonnes CO2e)'])

plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis, color='blue', marker='o')

for j, value in enumerate(y_axis):
    plt.text(x_axis[j], value, f'{value/1_000_000:.2f}', ha='left')

plt.grid(True)
plt.xticks(x_axis)
plt.title('British Columbia Total CO₂e Emission (Million tonnes)')
bc_totals_png = os.path.join(OUT_DIR, "bc_totals_trend.png")
plt.tight_layout()
plt.savefig(bc_totals_png, dpi=200)
plt.show()

# ==========================================
# Part 2: Top 10 sectors stacked area over time
# ==========================================
bc_sector_year = (
    bc_emission
    .groupby(['Reference Year', 'Facility Description'])['Total Emissions (tonnes CO2e)']
    .sum()
    .reset_index()
)

total_emissions_per_sector = (
    bc_sector_year.groupby('Facility Description')['Total Emissions (tonnes CO2e)']
    .sum()
    .sort_values(ascending=False)
)
top_10_sectors = total_emissions_per_sector.head(10).index.tolist()

filtered_df = bc_sector_year[bc_sector_year['Facility Description'].isin(top_10_sectors)]

pivot_df = (
    filtered_df
    .pivot(index='Reference Year', columns='Facility Description', values='Total Emissions (tonnes CO2e)')
    .fillna(0)
)

plt.figure(figsize=(14, 7))
pivot_df.plot(kind='area', stacked=True, figsize=(14, 7), colormap='tab20', linewidth=0)
plt.title("British Columbia: Emissions by Top 10 Sectors Over Time")
plt.xlabel("Year")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.xticks(ticks=pivot_df.index, labels=pivot_df.index.astype(int))
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
sectors_area_png = os.path.join(OUT_DIR, "bc_top10_sectors_area.png")
plt.savefig(sectors_area_png, dpi=200)
plt.show()

# ====================================================
# Part 3: Actual vs Targets (2007 baseline) line chart
# ====================================================
bc_total_by_year = (
    bc_emission.groupby('Reference Year')['Total Emissions (tonnes CO2e)']
    .sum().reset_index()
)
bc_total_by_year['Mt CO2e'] = bc_total_by_year['Total Emissions (tonnes CO2e)'] / 1_000_000

baseline_year = 2007
baseline_value = bc_total_by_year.loc[
    bc_total_by_year['Reference Year'] == baseline_year, 'Mt CO2e'
].values[0]

targets = {
    2025: 0.84,  # 16% reduction
    2030: 0.60,  # 40% reduction
    2040: 0.40,  # 60% reduction
    2050: 0.20,  # 80% reduction
}

last_actual_year = bc_total_by_year['Reference Year'].max()
target_years = [baseline_year, last_actual_year] + list(targets.keys())
target_values = [
    baseline_value,
    bc_total_by_year.loc[bc_total_by_year['Reference Year'] == last_actual_year, 'Mt CO2e'].values[0],
] + [baseline_value * pct for pct in targets.values()]

plt.figure(figsize=(12, 7))
plt.plot(
    bc_total_by_year['Reference Year'],
    bc_total_by_year['Mt CO2e'],
    marker='o', color='#1f77b4', linewidth=2, markersize=4, label='Actual Emissions'
)
plt.plot(
    target_years, target_values,
    linestyle='--', color='#2ca02c', marker='o', markersize=8, linewidth=2, label='Target Trajectory'
)

for year, y_val, pct in zip(list(targets.keys()), target_values[2:], targets.values()):
    reduction_pct = int((1 - pct) * 100)
    plt.annotate(f"{reduction_pct}% reduction", (year, y_val),
                 textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9, color='#2ca02c')

plt.axhline(y=baseline_value, color='gray', linestyle=':', alpha=0.5, label='2007 Baseline')
for val in target_values[2:]:
    plt.axhline(y=val, color='gray', linestyle=':', alpha=0.3)

plt.title('British Columbia GHG Emissions: Actual vs. Targets (2007 Baseline)', fontsize=14, pad=20)
plt.xlabel('Year'); plt.ylabel('Megatonnes CO₂e')
plt.legend(loc='upper right', framealpha=1)
plt.grid(True, linestyle='--', alpha=0.3)

min_year = min(bc_total_by_year['Reference Year'].min(), baseline_year) - 1
max_year = 2051
plt.xticks(np.arange(min_year, max_year, 5))
plt.xlim(min_year, max_year)
plt.ylim(0, max(bc_total_by_year['Mt CO2e'].max(), baseline_value) * 1.1)

plt.figtext(0.5, 0.01, "Data source: Your dataset", ha="center", fontsize=9, alpha=0.7)
plt.tight_layout()
targets_png = os.path.join(OUT_DIR, "bc_actual_vs_targets.png")
plt.savefig(targets_png, dpi=200)
plt.show()

# ===========================================
# Part 4: Print 2050 target (80% below 2007)
# ===========================================
baseline_2007 = bc_emission[bc_emission['Reference Year'] == 2007]['Total Emissions (tonnes CO2e)'].sum()
target_2050 = baseline_2007 * (1 - 0.80)
print(f"BC's 2050 emissions target: {target_2050/1_000_000:.2f} million tonnes CO2e")

# =======================================================
# Part 5: Top 15 most emission-intensive facilities (avg)
# =======================================================
tmp = bc_emission.copy()
tmp['Total Emissions (tonnes CO2e)'] = pd.to_numeric(tmp['Total Emissions (tonnes CO2e)'], errors='coerce')

facility_avg = tmp.groupby('Facility Name')['Total Emissions (tonnes CO2e)'].agg(['sum', 'count'])
facility_avg['Avg Emissions per Year'] = facility_avg['sum'] / facility_avg['count']
top_emitters = facility_avg.sort_values('Avg Emissions per Year', ascending=False).head(15)

plt.figure(figsize=(12, 6))
plt.barh(top_emitters.index, top_emitters['Avg Emissions per Year'] / 1e6, color='gold')
plt.xlabel('Average Annual Emissions (Million tonnes CO2e)')
plt.title('Top 15 Emission-Intensive Facilities in BC')
plt.gca().invert_yaxis()
plt.grid(axis='x')
plt.tight_layout()
emitters_png = os.path.join(OUT_DIR, "bc_top15_facilities.png")
plt.savefig(emitters_png, dpi=200)
plt.show()

# ============================================================
# Part 6: BC vs Canada – emissions + BC share (%) over time
# ============================================================
bc_yearly = bc_emission.groupby('Reference Year')['Total Emissions (tonnes CO2e)'].sum().reset_index(name='BC Emissions')
canada_yearly = emission_df.groupby('Reference Year')['Total Emissions (tonnes CO2e)'].sum().reset_index(name='Canada Emissions')

comparison_df = pd.merge(bc_yearly, canada_yearly, on='Reference Year')
comparison_df['BC Share (%)'] = (comparison_df['BC Emissions'] / comparison_df['Canada Emissions']) * 100

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(comparison_df['Reference Year'], comparison_df['Canada Emissions'] / 1e6, label='Canada Emissions', color='blue')
ax1.plot(comparison_df['Reference Year'], comparison_df['BC Emissions'] / 1e6, label='BC Emissions', color='green')
ax1.set_xlabel('Year'); ax1.set_ylabel('Emissions (Million tonnes CO2e)')
ax1.set_title('British Columbia vs Canada: GHG Emissions and Contribution Share')
ax1.legend(loc='upper left'); ax1.grid(True)

ax2 = ax1.twinx()
ax2.plot(comparison_df['Reference Year'], comparison_df['BC Share (%)'], color='red', linestyle='--', label='BC Share of Canada (%)')
ax2.set_ylabel('BC Share of National Emissions (%)')
ax2.legend(loc='upper right')

plt.xticks(ticks=comparison_df['Reference Year'], labels=comparison_df['Reference Year'].astype(int))
plt.tight_layout()
bc_vs_canada_png = os.path.join(OUT_DIR, "bc_vs_canada.png")
plt.savefig(bc_vs_canada_png, dpi=200)
plt.show()
