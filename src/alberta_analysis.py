import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------- Robust paths (works no matter where you run from) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/Alberta")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv  = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")

prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")


# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Ensure numeric columns are numeric (safe coercion)
for col in ["Total Emissions (tonnes CO2e)", "CH4 (tonnes CO2e)"]:
    if col in emission_df.columns:
        emission_df[col] = pd.to_numeric(emission_df[col], errors="coerce")

# =====================================================
# Part 0: Alberta overall slice + Alberta targets table
# =====================================================
alberta_overall_df = emission_df[emission_df["Facility Province"] == "Alberta"].copy()
alberta_targets_df = provincial_targets_df[provincial_targets_df["Province"] == "Alberta"].copy()

alberta_overall_path = os.path.join(OUT_DIR, "ab_overall_facility_rows.csv")
alberta_targets_path = os.path.join(OUT_DIR, "ab_targets_table.csv")
alberta_overall_df.to_csv(alberta_overall_path, index=False)
alberta_targets_df.to_csv(alberta_targets_path, index=False)

print(f"Saved Alberta facility rows → {alberta_overall_path}")
print(f"Saved Alberta targets table → {alberta_targets_path}")

# ==========================================
# Part 1: Total CH4 by year (Alberta only)
# =======================================
ch4_year = (
    alberta_overall_df
    .groupby("Reference Year", as_index=False)[["CH4 (tonnes CO2e)"]]
    .sum()
    .rename(columns={"CH4 (tonnes CO2e)": "Total CH4 (tonnes CO2e)"})
    .sort_values("Reference Year")
)

ch4_year_csv = os.path.join(OUT_DIR, "ab_ch4_by_year.csv")
ch4_year.to_csv(ch4_year_csv, index=False)
print(f"Saved AB CH4 by year → {ch4_year_csv}")

# Plot CH4 trend
plt.figure(figsize=(10, 6))
plt.plot(ch4_year["Reference Year"], ch4_year["Total CH4 (tonnes CO2e)"], marker="o")
plt.title("Alberta — Total CH4 Emissions Over Years")
plt.xlabel("Reference Year")
plt.ylabel("Total CH4 (tonnes CO2e)")
plt.grid(True)
plt.xticks(ch4_year["Reference Year"], rotation=45)
plt.tight_layout()
ab_ch4_trend_png = os.path.join(OUT_DIR, "ab_ch4_trend.png")
plt.savefig(ab_ch4_trend_png, dpi=200)
plt.show()

# ==========================================================
# Part 2: % change in CH4 relative to 2014 (2014 and later)
# ==========================================================
if (ch4_year["Reference Year"] == 2014).any():
    ch4_2014_value = ch4_year.loc[ch4_year["Reference Year"] == 2014, "Total CH4 (tonnes CO2e)"].values[0]
    ch4_year_from_2014 = ch4_year[ch4_year["Reference Year"] >= 2014].copy()
    ch4_year_from_2014["% Change from 2014"] = (
        (ch4_year_from_2014["Total CH4 (tonnes CO2e)"] - ch4_2014_value) / ch4_2014_value * 100.0
    )

    ab_ch4_pct_csv = os.path.join(OUT_DIR, "ab_ch4_pct_change_from_2014.csv")
    ch4_year_from_2014.to_csv(ab_ch4_pct_csv, index=False)
    print(f"Saved AB CH4 % change (from 2014) → {ab_ch4_pct_csv}")

    plt.figure(figsize=(10, 6))
    plt.plot(ch4_year_from_2014["Reference Year"], ch4_year_from_2014["% Change from 2014"], marker="o")
    plt.title("Alberta — % Change in Total CH4 (tonnes CO2e) from 2014")
    plt.xlabel("Reference Year")
    plt.ylabel("% Change from 2014")
    plt.grid(True)
    plt.xticks(ch4_year_from_2014["Reference Year"])
    plt.axhline(0, color="red", linestyle="--")
    plt.tight_layout()
    ab_ch4_pct_png = os.path.join(OUT_DIR, "ab_ch4_pct_change_from_2014.png")
    plt.savefig(ab_ch4_pct_png, dpi=200)
    plt.show()
else:
    print("⚠️ 2014 not present in data; skipping % change from 2014 plot/table.")

# ==================================================================================
# Part 3: Top 10 Facility *Descriptions* by avg CH4 (2017–2023), descending
# ==================================================================================
mask_17_23 = (alberta_overall_df["Reference Year"] >= 2017) & (alberta_overall_df["Reference Year"] <= 2023)
ab_17_23 = alberta_overall_df.loc[mask_17_23, ["Facility Description", "CH4 (tonnes CO2e)"]].copy()

ch4_emissions_avg = (
    ab_17_23.groupby("Facility Description", as_index=False)["CH4 (tonnes CO2e)"]
    .mean()
    .rename(columns={"CH4 (tonnes CO2e)": "Average CH4 Emissions"})
    .sort_values("Average CH4 Emissions", ascending=False)
    .head(10)
)

ab_ch4_avg_csv = os.path.join(OUT_DIR, "ab_top10_avg_ch4_by_facility_description_2017_2023.csv")
ch4_emissions_avg.to_csv(ab_ch4_avg_csv, index=False)
print(f"Saved AB top-10 avg CH4 (2017–2023) → {ab_ch4_avg_csv}")

plt.figure(figsize=(10, 6))
plt.barh(ch4_emissions_avg["Facility Description"], ch4_emissions_avg["Average CH4 Emissions"], color="skyblue")
plt.xlabel("Average CH4 Emissions (tonnes CO2e)")
plt.title("Top 10 Facility Descriptions by Average CH4 Emissions (2017–2023) — Alberta")
plt.gca().invert_yaxis()
plt.tight_layout()
ab_top10_ch4_png = os.path.join(OUT_DIR, "ab_top10_avg_ch4_facility_desc_2017_2023.png")
plt.savefig(ab_top10_ch4_png, dpi=200)
plt.show()

# =======================================================================================
# Part 4: In-situ vs Mined oil sands — total emissions (not just CH4) grouped by year
# =======================================================================================
filtered_facilities = alberta_overall_df[
    alberta_overall_df["Facility Description"].isin(["In-situ oil sands extraction", "Mined oil sands extraction"])
].copy()

grouped_facilities = (
    filtered_facilities
    .groupby(["Reference Year", "Facility Description"], as_index=False)["Total Emissions (tonnes CO2e)"]
    .sum()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Emissions Sum"})
)

ab_oilsands_csv = os.path.join(OUT_DIR, "ab_oilsands_insitu_vs_mined_by_year.csv")
grouped_facilities.to_csv(ab_oilsands_csv, index=False)
print(f"Saved AB oil sands (in-situ vs mined) by year → {ab_oilsands_csv}")

# Plot both series on one chart (lines per facility description)
plt.figure(figsize=(10, 6))
for desc, sub in grouped_facilities.groupby("Facility Description"):
    sub_sorted = sub.sort_values("Reference Year")
    plt.plot(sub_sorted["Reference Year"], sub_sorted["Total Emissions Sum"], marker="o", label=desc)

plt.title("Alberta — In-situ vs Mined Oil Sands: Total Emissions Over Years")
plt.xlabel("Reference Year")
plt.ylabel("Total Emissions Sum (tonnes CO2e)")
plt.grid(True)
plt.xticks(sorted(grouped_facilities["Reference Year"].unique()))
plt.legend()
plt.tight_layout()
ab_oilsands_png = os.path.join(OUT_DIR, "ab_oilsands_insitu_vs_mined_trend.png")
plt.savefig(ab_oilsands_png, dpi=200)
plt.show()