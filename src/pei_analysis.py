import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/PEI")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")
prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")

# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Ensure numeric columns are numeric (safe coercion)
if "Total Emissions (tonnes CO2e)" in emission_df.columns:
    emission_df["Total Emissions (tonnes CO2e)"] = pd.to_numeric(
        emission_df["Total Emissions (tonnes CO2e)"], errors="coerce"
    )

# =========================================================
# Part 1 — PEI totals by year
# =========================================================
pei_emission = emission_df[emission_df["Facility Province"] == "Prince Edward Island"].copy()

grouped_pei_emission = (
    pei_emission
    .groupby("Reference Year")[["Total Emissions (tonnes CO2e)"]]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "PEI Total Emission (tonnes CO2e)"})
)
grouped_pei_emission["PEI Total Emission (tonnes CO2e)"] = (
    grouped_pei_emission["PEI Total Emission (tonnes CO2e)"].round(2)
)

pei_totals_csv = os.path.join(OUT_DIR, "pei_total_emissions_by_year.csv")
grouped_pei_emission.to_csv(pei_totals_csv, index=False)
print(f"Saved PEI totals by year → {pei_totals_csv}")

# ---- Plot: totals in kilotonnes (kt) per your code ----
x_axis = np.array(grouped_pei_emission["Reference Year"])
y_axis_kt = np.array(grouped_pei_emission["PEI Total Emission (tonnes CO2e)"] / 1000.0)

plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis_kt, color="blue", marker="o")
for j, value in enumerate(y_axis_kt):
    plt.text(x_axis[j], value, f"{value:.2f}", ha="right")

plt.grid(True)
plt.xticks(x_axis)
plt.title("Prince Edward Island Total CO₂e Emission (kilotonnes, kt) / Year")
plt.tight_layout()
pei_trend_kt_png = os.path.join(OUT_DIR, "pei_total_emissions_trend_kt.png")
plt.savefig(pei_trend_kt_png, dpi=200)
plt.show()
print(f"Saved PEI trend (kt) → {pei_trend_kt_png}")

# =========================================================
# Part 2 — Targets & linear path (mirrors your logic)
# =========================================================
# Targets table slice
pei_target = provincial_targets_df[provincial_targets_df["Province"] == "Prince Edward Island"].copy()
pei_targets_csv = os.path.join(OUT_DIR, "pei_targets_table.csv")
pei_target.to_csv(pei_targets_csv, index=False)
print(f"Saved PEI targets table → {pei_targets_csv}")

# Your baseline numbers (in *tonnes*)
baseline_year_emission_1990 = 1.78 * 1_000_000
baseline_reduction_in_tonnes = baseline_year_emission_1990 - (1.2 * 1_000_000)
annual_percentage_deduction = baseline_reduction_in_tonnes / (2030 - 1990)  # tonnes/year

# Baseline start point for year 2004 (in *tonnes*)
baseline_start_point = round(
    baseline_year_emission_1990 - ((2004 - 1990) * annual_percentage_deduction), 2
)

# Build target series aligned to the grouped years (keeps your indexing)
y_axis_target_tonnes = []
for x in range(len(grouped_pei_emission["Reference Year"])):
    y_axis_target_tonnes.append(baseline_start_point - (annual_percentage_deduction * x))

# Actual (tonnes) for overlay
x_axis = np.array(grouped_pei_emission["Reference Year"])
y_axis_tonnes = np.array(grouped_pei_emission["PEI Total Emission (tonnes CO2e)"])

# Save the target vs actual as CSV (tonnes)
pei_targets_series_csv = os.path.join(OUT_DIR, "pei_actual_vs_target_tonnes.csv")
pd.DataFrame({
    "Reference Year": x_axis,
    "Actual (tonnes CO2e)": y_axis_tonnes,
    "Target (tonnes CO2e)": y_axis_target_tonnes
}).to_csv(pei_targets_series_csv, index=False)
print(f"Saved PEI actual vs target series (tonnes) → {pei_targets_series_csv}")

# Plot actual vs target (both in *tonnes*, to avoid unit mismatch)
plt.figure(figsize=(12, 6))
plt.plot(x_axis, y_axis_tonnes, color="blue", marker="o", label="Actual Emission")
plt.plot(x_axis, y_axis_target_tonnes, color="green", linestyle="--", label="Target Emission")

plt.grid(True)
plt.xticks(x_axis)
plt.title("Prince Edward Island Total CO₂e Emission (tonnes) / Year")
plt.legend()
plt.tight_layout()
pei_trend_targets_png = os.path.join(OUT_DIR, "pei_total_emissions_actual_vs_target_tonnes.png")
plt.savefig(pei_trend_targets_png, dpi=200)
plt.show()
print(f"Saved PEI actual vs target (tonnes) → {pei_trend_targets_png}")

# =========================================================
# Part 3 — Facility breakdown & heatmap
# =========================================================
grouped_pei_facility = (
    pei_emission
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
grouped_pei_facility["Total Facility Emission (tonnes CO2e)"] = (
    grouped_pei_facility["Total Facility Emission (tonnes CO2e)"].round(2)
)

pei_facility_csv = os.path.join(OUT_DIR, "pei_facility_emissions_by_year.csv")
grouped_pei_facility.to_csv(pei_facility_csv, index=False)
print(f"Saved PEI facility-by-year table → {pei_facility_csv}")

pivot_group_pei_facilities = grouped_pei_facility.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).reset_index().fillna(0)

# Ensure numeric for pivot value columns
if pivot_group_pei_facilities.shape[1] > 1:
    pivot_group_pei_facilities.iloc[:, 1:] = pivot_group_pei_facilities.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")

# Save pivot as CSV (handy for README)
pei_facility_pivot_csv = os.path.join(OUT_DIR, "pei_facility_emissions_pivot.csv")
pivot_group_pei_facilities.to_csv(pei_facility_pivot_csv, index=False)
print(f"Saved PEI facility pivot → {pei_facility_pivot_csv}")

plt.figure(figsize=(12, 3))
matrix = pivot_group_pei_facilities.iloc[:, 1:].values

sns.heatmap(
    matrix,
    cmap="RdYlGn_r",
    annot=False,
    fmt=".2f",
    cbar_kws={"label": "CO2e Emission (tonnes CO₂e)"},
    xticklabels=pivot_group_pei_facilities.columns[1:],
    yticklabels=pivot_group_pei_facilities["Facility Description"],
    linewidths=.65, linecolor="white"
)
plt.title("PEI GHG Emissions by Facility")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.xticks(rotation=90)
plt.tight_layout()
pei_heatmap_png = os.path.join(OUT_DIR, "pei_facility_heatmap.png")
plt.savefig(pei_heatmap_png, dpi=200)
plt.show()
print(f"Saved PEI facility heatmap → {pei_heatmap_png}")
