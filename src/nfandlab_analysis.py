import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/NewfoundlandLabrador")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")

# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)

# Ensure numeric
if "Total Emissions (tonnes CO2e)" in emission_df.columns:
    emission_df["Total Emissions (tonnes CO2e)"] = pd.to_numeric(
        emission_df["Total Emissions (tonnes CO2e)"], errors="coerce"
    )

# =========================================================
# Part 1 — Facility heatmap (by year x facility)
# =========================================================
nl_emission_df = emission_df[emission_df["Facility Province"] == "Newfoundland and Labrador"].copy()

grouped_nl_facility = (
    nl_emission_df
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
grouped_nl_facility["Total Facility Emission (tonnes CO2e)"] = (
    grouped_nl_facility["Total Facility Emission (tonnes CO2e)"].round(2)
)

# Save table
nl_facility_csv = os.path.join(OUT_DIR, "nl_facility_emissions_by_year.csv")
grouped_nl_facility.to_csv(nl_facility_csv, index=False)
print(f"Saved Newfoundland & Labrador facility-by-year table → {nl_facility_csv}")

# Pivot for heatmap
nl_pivot = grouped_nl_facility.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).reset_index().fillna(0)

# Ensure numeric across value columns
if nl_pivot.shape[1] > 1:
    nl_pivot.iloc[:, 1:] = nl_pivot.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")

# Save pivot
nl_pivot_csv = os.path.join(OUT_DIR, "nl_facility_emissions_pivot.csv")
nl_pivot.to_csv(nl_pivot_csv, index=False)
print(f"Saved Newfoundland & Labrador facility pivot → {nl_pivot_csv}")

# Heatmap
plt.figure(figsize=(12, 6))
matrix = nl_pivot.iloc[:, 1:].values
sns.heatmap(
    matrix,
    cmap="RdYlGn_r",
    annot=False,
    fmt=".2f",
    cbar_kws={"label": "CO2e Emission (tonnes CO₂e)"},
    xticklabels=nl_pivot.columns[1:],
    yticklabels=nl_pivot["Facility Description"],
    linewidths=.65, linecolor="white"
)
plt.title("Newfoundland & Labrador GHG Emissions by Facility")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.xticks(rotation=90)
plt.tight_layout()
nl_heatmap_png = os.path.join(OUT_DIR, "nl_facility_heatmap.png")
plt.savefig(nl_heatmap_png, dpi=200)
plt.show()
print(f"Saved NL facility heatmap → {nl_heatmap_png}")

# =========================================================
# Part 2 — Total emissions by year + trendline
# =========================================================
nl_totals_by_year = (
    nl_emission_df
    .groupby("Reference Year")["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .sort_values("Reference Year")
)

# Save totals-by-year
nl_totals_csv = os.path.join(OUT_DIR, "nl_total_emissions_by_year.csv")
nl_totals_by_year.to_csv(nl_totals_csv, index=False)
print(f"Saved NL totals by year → {nl_totals_csv}")

# Plot with trendline
years = nl_totals_by_year["Reference Year"].to_numpy()
vals  = nl_totals_by_year["Total Emissions (tonnes CO2e)"].to_numpy()

plt.figure(figsize=(10, 6))
plt.plot(years, vals, marker="o", linestyle="-", color="r", label="Total Emissions")
if len(years) >= 2:
    z = np.polyfit(years, vals, 1)
    p = np.poly1d(z)
    plt.plot(years, p(years), linestyle="--", color="r", label="Trendline")
else:
    print("⚠️ Not enough points to compute a trendline.")
plt.title("Total Emissions by Year in Newfoundland & Labrador")
plt.xlabel("Reference Year")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.grid(True)
plt.legend()
plt.tight_layout()
nl_trend_png = os.path.join(OUT_DIR, "nl_total_emissions_trendline.png")
plt.savefig(nl_trend_png, dpi=200)
plt.show()
print(f"Saved NL trend plot → {nl_trend_png}")

# =========================================================
# Part 3 — Linear trajectory (baseline 2005 → 2030, 30% cut)
# (standalone: define these here instead of reusing external vars)
# =========================================================
baseline_year = 2005
target_year = 2030
percent_reduction = 0.30  # 30% reduction
years_traj = list(range(baseline_year, target_year + 1))

# Baseline emission for 2005 (sum across facilities)
baseline_emission_nl = (
    grouped_nl_facility.loc[grouped_nl_facility["Reference Year"] == baseline_year, "Total Facility Emission (tonnes CO2e)"]
    .sum()
)

if pd.isna(baseline_emission_nl) or baseline_emission_nl == 0:
    print("⚠️ 2005 baseline not found or zero; skipping trajectory computation.")
else:
    target_emission_nl = baseline_emission_nl * (1 - percent_reduction)

    emissions_nl = [
        baseline_emission_nl - (baseline_emission_nl - target_emission_nl) * (yr - baseline_year) / (target_year - baseline_year)
        for yr in years_traj
    ]

    trajectory_df_nl = pd.DataFrame({"Year": years_traj, "Emission (tonnes CO2e)": emissions_nl})

    # Save trajectory
    nl_traj_csv = os.path.join(OUT_DIR, "nl_trajectory_2005_to_2030.csv")
    trajectory_df_nl.to_csv(nl_traj_csv, index=False)
    print(f"Saved NL reduction trajectory → {nl_traj_csv}")

    # Plot trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(trajectory_df_nl["Year"], trajectory_df_nl["Emission (tonnes CO2e)"], marker="o", linestyle="-", color="r")
    plt.title("Newfoundland & Labrador Emission Reduction Trajectory")
    plt.xlabel("Year")
    plt.ylabel("Emission (tonnes CO2e)")
    plt.grid(True)
    plt.tight_layout()
    nl_traj_png = os.path.join(OUT_DIR, "nl_trajectory_2005_to_2030.png")
    plt.savefig(nl_traj_png, dpi=200)
    plt.show()
    print(f"Saved NL trajectory plot → {nl_traj_png}")

    # =========================================================
    # Part 4 — Actual vs trajectory overlay
    # =========================================================
    actual_yearly_nl = (
        grouped_nl_facility.groupby("Reference Year")["Total Facility Emission (tonnes CO2e)"].sum().reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(actual_yearly_nl["Reference Year"], actual_yearly_nl["Total Facility Emission (tonnes CO2e)"],
             marker="o", linestyle="-", color="g", label="Actual Emissions")
    plt.plot(trajectory_df_nl["Year"], trajectory_df_nl["Emission (tonnes CO2e)"],
             marker="o", linestyle="-", color="r", label="Target")
    plt.title("Newfoundland & Labrador: Actual Emissions vs Reduction Trajectory")
    plt.xlabel("Year")
    plt.ylabel("Emission (tonnes CO2e)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    nl_overlay_png = os.path.join(OUT_DIR, "nl_actual_vs_trajectory.png")
    plt.savefig(nl_overlay_png, dpi=200)
    plt.show()
    print(f"Saved NL overlay plot → {nl_overlay_png}")
