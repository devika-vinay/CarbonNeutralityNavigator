import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/NovaScotia")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")
prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")

# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Ensure numeric columns are numeric
if "Total Emissions (tonnes CO2e)" in emission_df.columns:
    emission_df["Total Emissions (tonnes CO2e)"] = pd.to_numeric(
        emission_df["Total Emissions (tonnes CO2e)"], errors="coerce"
    )

# =========================================================
# Part 1 — Segmentation & Trend (NS totals per year + 2030)
# =========================================================
nova_scotia_emission = emission_df[emission_df["Facility Province"] == "Nova Scotia"].copy()

grouped_nova_scotia_emission = (
    nova_scotia_emission
    .groupby("Reference Year")[["Total Emissions (tonnes CO2e)"]]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Nova Scotia Total Emission (tonnes CO2e)"})
)
grouped_nova_scotia_emission["Nova Scotia Total Emission (tonnes CO2e)"] = (
    grouped_nova_scotia_emission["Nova Scotia Total Emission (tonnes CO2e)"].round(2)
)

ns_totals_csv = os.path.join(OUT_DIR, "ns_total_emissions_by_year.csv")
grouped_nova_scotia_emission.to_csv(ns_totals_csv, index=False)
print(f"Saved NS totals by year → {ns_totals_csv}")

# Targets slice
nova_scotia_target = provincial_targets_df[
    provincial_targets_df["Province"] == "Nova Scotia"
].reset_index(drop=True)
ns_targets_csv = os.path.join(OUT_DIR, "ns_targets_table.csv")
nova_scotia_target.to_csv(ns_targets_csv, index=False)
print(f"Saved NS targets table → {ns_targets_csv}")

# Baseline emission (2005) and annualized reduction to 2030 (keep your logic)
can_plot_target_2030 = True
if (grouped_nova_scotia_emission["Reference Year"] == 2005).any() and \
   ("Reduction Upper Bound" in nova_scotia_target.columns) and \
   len(nova_scotia_target) >= 1:
    nova_scotia_reference_total_emission = grouped_nova_scotia_emission.loc[
        grouped_nova_scotia_emission["Reference Year"] == 2005,
        "Nova Scotia Total Emission (tonnes CO2e)"
    ].round(2).values[0]

    # Your annual target reduction definition
    nova_scotia_baseline_annual_target_reduction_2030 = int(nova_scotia_target["Reduction Upper Bound"][0]) / 25

    # Build axes & target array
    x_target_axis = np.array([x for x in grouped_nova_scotia_emission["Reference Year"]])
    y_target_axis_2030 = grouped_nova_scotia_emission["Nova Scotia Total Emission (tonnes CO2e)"].copy().to_numpy()

    # Apply reduction factor iteratively (preserve your loop style/indexing)
    reduction_factor_2030 = 1 - (nova_scotia_baseline_annual_target_reduction_2030 / 100)
    for i in range(2, len(y_target_axis_2030)):
        y_target_axis_2030[i] = y_target_axis_2030[i - 1] * reduction_factor_2030
else:
    print("⚠️ Could not compute NS 2030 target line (missing 2005 baseline or target info).")
    can_plot_target_2030 = False

# Plot: Actual vs 2030 target (Mt)
y_axis_million = np.array(grouped_nova_scotia_emission["Nova Scotia Total Emission (tonnes CO2e)"] / 1e6)
x_axis = np.array(grouped_nova_scotia_emission["Reference Year"])

plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis_million, color="blue", marker="o", label="Actual Emission")

if can_plot_target_2030:
    plt.plot(x_axis, y_target_axis_2030 / 1e6, color="green", linestyle="--", label="Target 2030")

for i, value in enumerate(y_axis_million):
    plt.text(x_axis[i], value, f"{value:.2f}", ha="right")

plt.grid(True)
plt.xticks(x_axis)
plt.title("Nova Scotia Total Emission (Megatonnes (Mt CO₂e)) / Year")
plt.legend()
plt.tight_layout()
ns_trend_png = os.path.join(OUT_DIR, "ns_total_emissions_trend_actual_vs_2030.png")
plt.savefig(ns_trend_png, dpi=200)
plt.show()
print(f"Saved NS trend plot → {ns_trend_png}")

# =================================
# Part 2 — Sector Dissection (Top 10)
# =================================
grouped_nova_scotia_facility = (
    nova_scotia_emission
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
grouped_nova_scotia_facility["Total Facility Emission (tonnes CO2e)"] = (
    grouped_nova_scotia_facility["Total Facility Emission (tonnes CO2e)"].round(2)
)

ns_facility_csv = os.path.join(OUT_DIR, "ns_facility_emissions_by_year.csv")
grouped_nova_scotia_facility.to_csv(ns_facility_csv, index=False)
print(f"Saved NS facility-by-year table → {ns_facility_csv}")

# Top 10 facilities by total across all years
facility_sums = grouped_nova_scotia_facility.groupby("Facility Description")["Total Facility Emission (tonnes CO2e)"].sum()
top_10_facilities = facility_sums.sort_values(ascending=False).head(10).index

df_top10 = grouped_nova_scotia_facility[
    grouped_nova_scotia_facility["Facility Description"].isin(top_10_facilities)
].copy()

emission_pivot = df_top10.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).fillna(0)

plt.figure(figsize=(12, 6))
ax = sns.heatmap(
    emission_pivot / 1e6,  # Convert to Mt
    cmap="RdYlGn_r",
    linecolor="white",
    linewidths=0.5,
    cbar_kws={"label": "CO2e Emission (Megatonnes (Mt CO₂e))"},
    annot=False,
    fmt=".2f",
)
plt.xticks(rotation=90)
plt.title("Nova Scotia Top 10 GHG Emission Facilities")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.tight_layout()
ns_heatmap_png = os.path.join(OUT_DIR, "ns_top10_facilities_heatmap.png")
plt.savefig(ns_heatmap_png, dpi=200)
plt.show()
print(f"Saved NS heatmap → {ns_heatmap_png}")
