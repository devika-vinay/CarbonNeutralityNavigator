import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/Ontario")
os.makedirs(OUT_DIR, exist_ok=True)

# Prefer cleaned CSVs if available
emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")
prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")

# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Ensure numeric
if "Total Emissions (tonnes CO2e)" in emission_df.columns:
    emission_df["Total Emissions (tonnes CO2e)"] = pd.to_numeric(
        emission_df["Total Emissions (tonnes CO2e)"], errors="coerce"
    )

# ====================================================
# Part 1: Totals by year + Targets (2030 + 2050)
# ====================================================
ontario_emission = emission_df[emission_df["Facility Province"] == "Ontario"].copy()

grouped_ontario_emission = (
    ontario_emission
    .groupby("Reference Year")[["Total Emissions (tonnes CO2e)"]]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Ontario Total Emission (tonnes CO2e)"})
)
grouped_ontario_emission["Ontario Total Emission (tonnes CO2e)"] = (
    grouped_ontario_emission["Ontario Total Emission (tonnes CO2e)"].round(2)
)

on_totals_csv = os.path.join(OUT_DIR, "on_total_emissions_by_year.csv")
grouped_ontario_emission.to_csv(on_totals_csv, index=False)
print(f"Saved Ontario totals by year → {on_totals_csv}")

# Targets table slice
ontario_target = provincial_targets_df[
    provincial_targets_df["Province"] == "Ontario"
].reset_index(drop=True)
on_targets_csv = os.path.join(OUT_DIR, "on_targets_table.csv")
ontario_target.to_csv(on_targets_csv, index=False)
print(f"Saved Ontario targets table → {on_targets_csv}")

# Baseline (2005)
can_plot_targets = True
if (grouped_ontario_emission["Reference Year"] == 2005).any() and \
   ("Reduction Upper Bound" in ontario_target.columns) and len(ontario_target) >= 2:
    ontario_reference_total_emission = grouped_ontario_emission.loc[
        grouped_ontario_emission["Reference Year"] == 2005,
        "Ontario Total Emission (tonnes CO2e)"
    ].round(2).values[0]

    ontario_baseline_annual_target_reduction_2030 = int(ontario_target["Reduction Upper Bound"][0]) / 25
    ontario_baseline_annual_target_reduction_2050 = round(int(ontario_target["Reduction Upper Bound"][1]) / 45, 2)

    x_target_axis = np.array(grouped_ontario_emission["Reference Year"])
    y_target_axis_2030 = grouped_ontario_emission["Ontario Total Emission (tonnes CO2e)"].copy().to_numpy()
    y_target_axis_2050 = grouped_ontario_emission["Ontario Total Emission (tonnes CO2e)"].copy().to_numpy()

    reduction_factor_2030 = 1 - (ontario_baseline_annual_target_reduction_2030 / 100)
    reduction_factor_2050 = 1 - (ontario_baseline_annual_target_reduction_2050 / 100)

    for i in range(2, len(y_target_axis_2030)):
        y_target_axis_2030[i] = y_target_axis_2030[i-1] * reduction_factor_2030
    for i in range(2, len(y_target_axis_2050)):
        y_target_axis_2050[i] = y_target_axis_2050[i-1] * reduction_factor_2050
else:
    print("Could not compute Ontario targets (missing baseline or target info).")
    can_plot_targets = False

# Plot trend
y_axis_million = grouped_ontario_emission["Ontario Total Emission (tonnes CO2e)"] / 1e6
x_axis = grouped_ontario_emission["Reference Year"]

plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis_million, color="blue", marker="o", label="Actual Emission")

if can_plot_targets:
    plt.plot(x_axis, y_target_axis_2030 / 1e6, color="green", linestyle="--", label="Target 2030")
    plt.plot(x_axis, y_target_axis_2050 / 1e6, color="red", linestyle="--", label="Target 2050")

for i, value in enumerate(y_axis_million):
    plt.text(x_axis.iloc[i], value, f"{value:.2f}", ha="right")

plt.grid(True)
plt.xticks(x_axis)
plt.title("Ontario Total Emission (Megatonnes (Mt CO₂e)) / Year")
plt.legend()
plt.tight_layout()
on_trend_png = os.path.join(OUT_DIR, "on_total_emissions_trend_actual_vs_targets.png")
plt.savefig(on_trend_png, dpi=200)
plt.show()
print(f"Saved Ontario trend plot → {on_trend_png}")

# ====================================================
# Part 2: Sector Dissection (Top 10 facilities)
# ====================================================
grouped_ontario_facility = (
    ontario_emission
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
grouped_ontario_facility["Total Facility Emission (tonnes CO2e)"] = (
    grouped_ontario_facility["Total Facility Emission (tonnes CO2e)"].round(2)
)

on_facility_csv = os.path.join(OUT_DIR, "on_facility_emissions_by_year.csv")
grouped_ontario_facility.to_csv(on_facility_csv, index=False)
print(f"Saved Ontario facility-by-year table → {on_facility_csv}")

# Top 10 facilities
facility_sums = grouped_ontario_facility.groupby("Facility Description")["Total Facility Emission (tonnes CO2e)"].sum()
top_10_facilities = facility_sums.sort_values(ascending=False).head(10).index

df_top10 = grouped_ontario_facility[grouped_ontario_facility["Facility Description"].isin(top_10_facilities)].copy()
emission_pivot = df_top10.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).fillna(0)

plt.figure(figsize=(12, 6))
sns.heatmap(
    emission_pivot / 1e6,  # convert to Mt
    cmap="RdYlGn_r",
    linecolor="white",
    linewidths=0.5,
    cbar_kws={"label": "CO2e Emission (Megatonnes (Mt CO₂e))"},
    annot=False,
    fmt=".2f"
)
plt.xticks(rotation=90)
plt.title("Ontario Top 10 GHG Emission Facilities")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.tight_layout()
on_heatmap_png = os.path.join(OUT_DIR, "on_top10_facilities_heatmap.png")
plt.savefig(on_heatmap_png, dpi=200)
plt.show()
print(f"Saved Ontario heatmap → {on_heatmap_png}")
