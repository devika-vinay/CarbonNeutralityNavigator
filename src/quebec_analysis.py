import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/Quebec")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")

# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)

# Ensure numeric (safe coercion)
if "Total Emissions (tonnes CO2e)" in emission_df.columns:
    emission_df["Total Emissions (tonnes CO2e)"] = pd.to_numeric(
        emission_df["Total Emissions (tonnes CO2e)"], errors="coerce"
    )

# =========================================================
# Part 1 — Facility heatmap (by year x facility)
# =========================================================
quebec_emission_df = emission_df[emission_df["Facility Province"] == "Quebec"].copy()

grouped_quebec_facility = (
    quebec_emission_df
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
grouped_quebec_facility["Total Facility Emission (tonnes CO2e)"] = (
    grouped_quebec_facility["Total Facility Emission (tonnes CO2e)"].round(2)
)

# Save facility-by-year table
qc_facility_csv = os.path.join(OUT_DIR, "qc_facility_emissions_by_year.csv")
grouped_quebec_facility.to_csv(qc_facility_csv, index=False)
print(f"Saved Quebec facility-by-year table → {qc_facility_csv}")

# Pivot (Facility x Year)
pivot_group_quebec_facilities = grouped_quebec_facility.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).reset_index().fillna(0)

# Ensure numeric across value columns
if pivot_group_quebec_facilities.shape[1] > 1:
    pivot_group_quebec_facilities.iloc[:, 1:] = pivot_group_quebec_facilities.iloc[:, 1:].apply(
        pd.to_numeric, errors="coerce"
    )

# Save pivot for README/reference
qc_facility_pivot_csv = os.path.join(OUT_DIR, "qc_facility_emissions_pivot.csv")
pivot_group_quebec_facilities.to_csv(qc_facility_pivot_csv, index=False)
print(f"Saved Quebec facility pivot → {qc_facility_pivot_csv}")

# Heatmap
plt.figure(figsize=(12, 12))  # Taller to fit many facilities
matrix = pivot_group_quebec_facilities.iloc[:, 1:].values
sns.heatmap(
    matrix,
    cmap="RdYlGn_r",
    annot=False,
    fmt=".2f",
    cbar_kws={"label": "CO2e Emission (tonnes CO₂e)"},
    xticklabels=pivot_group_quebec_facilities.columns[1:],
    yticklabels=pivot_group_quebec_facilities["Facility Description"],
    linewidths=.65, linecolor="white"
)
plt.title("Quebec GHG Emissions by Facility")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.xticks(rotation=90)
plt.tight_layout()
qc_heatmap_png = os.path.join(OUT_DIR, "qc_facility_heatmap.png")
plt.savefig(qc_heatmap_png, dpi=200)
plt.show()
print(f"Saved Quebec facility heatmap → {qc_heatmap_png}")

# =========================================================
# Part 2 — Total emissions by year + trendline
# =========================================================
total_quebec_emission_by_year = (
    quebec_emission_df
    .groupby("Reference Year")["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index(name="Quebec Emissions")
    .sort_values("Reference Year")
)

# Save totals-by-year table
qc_totals_csv = os.path.join(OUT_DIR, "qc_total_emissions_by_year.csv")
total_quebec_emission_by_year.to_csv(qc_totals_csv, index=False)
print(f"Saved Quebec totals by year → {qc_totals_csv}")

# Plot with trendline (guard if <2 points)
years = total_quebec_emission_by_year["Reference Year"].to_numpy()
vals  = total_quebec_emission_by_year["Quebec Emissions"].to_numpy()

plt.figure(figsize=(10, 6))
plt.plot(years, vals, marker="o", linestyle="-", color="b", label="Total Emissions")

if len(years) >= 2:
    z = np.polyfit(years, vals, 1)
    p = np.poly1d(z)
    plt.plot(years, p(years), linestyle="--", color="r", label="Trendline")
else:
    print("⚠️ Not enough data points to compute a trendline for Quebec.")

plt.title("Quebec Total Emissions by Year")
plt.xlabel("Year")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.legend()
plt.grid(True)
plt.tight_layout()
qc_trend_png = os.path.join(OUT_DIR, "qc_total_emissions_trendline.png")
plt.savefig(qc_trend_png, dpi=200)
plt.show()
print(f"Saved Quebec trend plot → {qc_trend_png}")
