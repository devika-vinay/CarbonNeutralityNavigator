import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/Saskatchewan")
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
saskatchewan_emission_df = emission_df[emission_df["Facility Province"] == "Saskatchewan"].copy()
sk_facility_by_year = (
    saskatchewan_emission_df
    .groupby(["Reference Year", "Facility Description"])["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Facility Emission (tonnes CO2e)"})
)
sk_facility_by_year["Total Facility Emission (tonnes CO2e)"] = (
    sk_facility_by_year["Total Facility Emission (tonnes CO2e)"].round(2)
)

# Save table
sk_facility_csv = os.path.join(OUT_DIR, "sk_facility_emissions_by_year.csv")
sk_facility_by_year.to_csv(sk_facility_csv, index=False)
print(f"Saved Saskatchewan facility-by-year table → {sk_facility_csv}")

# Pivot for heatmap
sk_pivot = sk_facility_by_year.pivot(
    index="Facility Description",
    columns="Reference Year",
    values="Total Facility Emission (tonnes CO2e)"
).reset_index().fillna(0)

# Ensure numeric across value columns
if sk_pivot.shape[1] > 1:
    sk_pivot.iloc[:, 1:] = sk_pivot.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")

# Save pivot
sk_pivot_csv = os.path.join(OUT_DIR, "sk_facility_emissions_pivot.csv")
sk_pivot.to_csv(sk_pivot_csv, index=False)
print(f"Saved Saskatchewan facility pivot → {sk_pivot_csv}")

# Heatmap
plt.figure(figsize=(12, 6))
matrix = sk_pivot.iloc[:, 1:].values
sns.heatmap(
    matrix,
    cmap="RdYlGn_r",
    annot=False,
    fmt=".2f",
    cbar_kws={"label": "CO2e Emission (tonnes CO₂e)"},
    xticklabels=sk_pivot.columns[1:],
    yticklabels=sk_pivot["Facility Description"],
    linewidths=.65, linecolor="white"
)
plt.title("Saskatchewan GHG Emissions by Facility")
plt.xlabel("Reference Year")
plt.ylabel("Facility Description")
plt.xticks(rotation=90)
plt.tight_layout()
sk_heatmap_png = os.path.join(OUT_DIR, "sk_facility_heatmap.png")
plt.savefig(sk_heatmap_png, dpi=200)
plt.show()
print(f"Saved Saskatchewan facility heatmap → {sk_heatmap_png}")

# =========================================================
# Part 2 — Total emissions by year + trendline
# =========================================================
sk_totals_by_year = (
    saskatchewan_emission_df
    .groupby("Reference Year")["Total Emissions (tonnes CO2e)"]
    .sum()
    .reset_index()
    .sort_values("Reference Year")
)

# Save totals-by-year
sk_totals_csv = os.path.join(OUT_DIR, "sk_total_emissions_by_year.csv")
sk_totals_by_year.to_csv(sk_totals_csv, index=False)
print(f"Saved Saskatchewan totals by year → {sk_totals_csv}")

# Plot with trendline
years = sk_totals_by_year["Reference Year"].to_numpy()
vals  = sk_totals_by_year["Total Emissions (tonnes CO2e)"].to_numpy()

plt.figure(figsize=(10, 6))
plt.plot(years, vals, marker="o", linestyle="-", color="g", label="Total Emissions")
if len(years) >= 2:
    z = np.polyfit(years, vals, 1)
    p = np.poly1d(z)
    plt.plot(years, p(years), linestyle="--", color="g", label="Trendline")
else:
    print("⚠️ Not enough points to compute a trendline.")
plt.title("Total Emissions by Year in Saskatchewan")
plt.xlabel("Reference Year")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.grid(True)
plt.legend()
plt.tight_layout()
sk_trend_png = os.path.join(OUT_DIR, "sk_total_emissions_trendline.png")
plt.savefig(sk_trend_png, dpi=200)
plt.show()
print(f"Saved Saskatchewan trend plot → {sk_trend_png}")

# =========================================================
# Part 3 — Linear trajectory (baseline 2005 → 2030, 30% cut)
# =========================================================
baseline_year = 2005
target_year = 2030
percent_reduction = 0.30  # 30% reduction

# Baseline emission for 2005 (sum across facilities)
baseline_emission = (
    sk_facility_by_year.loc[sk_facility_by_year["Reference Year"] == baseline_year, "Total Facility Emission (tonnes CO2e)"]
    .sum()
)

if pd.isna(baseline_emission) or baseline_emission == 0:
    print("⚠️ 2005 baseline not found or zero; skipping trajectory computation.")
else:
    target_emission = baseline_emission * (1 - percent_reduction)

    years_traj = list(range(baseline_year, target_year + 1))
    emissions_traj = [
        baseline_emission - (baseline_emission - target_emission) * (yr - baseline_year) / (target_year - baseline_year)
        for yr in years_traj
    ]

    trajectory_df = pd.DataFrame({"Year": years_traj, "Emission (tonnes CO2e)": emissions_traj})

    # Save trajectory
    sk_traj_csv = os.path.join(OUT_DIR, "sk_trajectory_2005_to_2030.csv")
    trajectory_df.to_csv(sk_traj_csv, index=False)
    print(f"Saved Saskatchewan reduction trajectory → {sk_traj_csv}")

    # Plot trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(trajectory_df["Year"], trajectory_df["Emission (tonnes CO2e)"], marker="o", linestyle="-", color="b")
    plt.title("Saskatchewan Emission Reduction Trajectory")
    plt.xlabel("Year")
    plt.ylabel("Emission (tonnes CO2e)")
    plt.grid(True)
    plt.tight_layout()
    sk_traj_png = os.path.join(OUT_DIR, "sk_trajectory_2005_to_2030.png")
    plt.savefig(sk_traj_png, dpi=200)
    plt.show()
    print(f"Saved Saskatchewan trajectory plot → {sk_traj_png}")

    # =========================================================
    # Part 4 — Actual vs trajectory overlay
    # =========================================================
    actual_yearly = (
        sk_facility_by_year.groupby("Reference Year")["Total Facility Emission (tonnes CO2e)"].sum().reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(actual_yearly["Reference Year"], actual_yearly["Total Facility Emission (tonnes CO2e)"],
             marker="o", linestyle="-", color="g", label="Actual Emissions")
    plt.plot(trajectory_df["Year"], trajectory_df["Emission (tonnes CO2e)"],
             marker="o", linestyle="-", color="b", label="Target")
    plt.title("Saskatchewan Emission Reduction Trajectory vs Actual Emissions")
    plt.xlabel("Year")
    plt.ylabel("Emission (tonnes CO2e)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    sk_overlay_png = os.path.join(OUT_DIR, "sk_actual_vs_trajectory.png")
    plt.savefig(sk_overlay_png, dpi=200)
    plt.show()
    print(f"Saved Saskatchewan overlay plot → {sk_overlay_png}")
