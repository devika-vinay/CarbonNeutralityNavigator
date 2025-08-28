import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Robust paths (run from anywhere) ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # project root
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "outputs/Manitoba")
os.makedirs(OUT_DIR, exist_ok=True)

emissions_csv = os.path.join(BASE_DIR, "outputs/Cleaned_GHGEmissions.csv")
prov_targets_csv = os.path.join(BASE_DIR, "outputs/Cleaned_ProvincialTargets.csv")


# ---------- Load data ----------
emission_df = pd.read_csv(emissions_csv)
provincial_targets_df = pd.read_csv(prov_targets_csv)

# Make sure key numeric columns are numeric
for col in ["Total Emissions (tonnes CO2e)"]:
    if col in emission_df.columns:
        emission_df[col] = pd.to_numeric(emission_df[col], errors="coerce")

# ===========================================================
# Part 0: Manitoba overall rows + Manitoba targets (tables)
# ===========================================================
manitoba_overall_df = emission_df[emission_df["Facility Province"] == "Manitoba"].copy()
manitoba_targets_df = provincial_targets_df[provincial_targets_df["Province"] == "Manitoba"].copy()

mb_overall_path = os.path.join(OUT_DIR, "mb_overall_facility_rows.csv")
mb_targets_path = os.path.join(OUT_DIR, "mb_targets_table.csv")
manitoba_overall_df.to_csv(mb_overall_path, index=False)
manitoba_targets_df.to_csv(mb_targets_path, index=False)

print(f"Saved Manitoba facility rows → {mb_overall_path}")
print(f"Saved Manitoba targets table → {mb_targets_path}")

# ==================================================================
# Part 1: Total emissions by Reference Year (equivalent to Spark sum)
# ==================================================================
manitoba_emissions_sum_df = (
    manitoba_overall_df
    .groupby("Reference Year", as_index=False)[["Total Emissions (tonnes CO2e)"]]
    .sum()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Emissions (tonnes CO2e) (sum)"})
    .sort_values("Reference Year")
)

mb_year_sum_csv = os.path.join(OUT_DIR, "mb_total_emissions_by_year.csv")
manitoba_emissions_sum_df.to_csv(mb_year_sum_csv, index=False)
print(f"Saved MB totals by year → {mb_year_sum_csv}")

# Plot: Total emissions over years (tonnes CO2e)
plt.figure(figsize=(10, 6))
plt.plot(
    manitoba_emissions_sum_df["Reference Year"],
    manitoba_emissions_sum_df["Total Emissions (tonnes CO2e) (sum)"],
    marker="o"
)
plt.title("Manitoba — Total Emissions Over Reference Years")
plt.xlabel("Reference Year")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.grid(True)
plt.xticks(manitoba_emissions_sum_df["Reference Year"])
plt.tight_layout()
mb_year_sum_png = os.path.join(OUT_DIR, "mb_total_emissions_by_year.png")
plt.savefig(mb_year_sum_png, dpi=200)
plt.show()

# =========================================================================================
# Part 2: Emissions by Facility Description for 2005 (descending) — Spark groupBy analogue
# =========================================================================================
mb_2005 = manitoba_overall_df[manitoba_overall_df["Reference Year"] == 2005]
manitoba_emissions_2005 = (
    mb_2005.groupby("Facility Description", as_index=False)["Total Emissions (tonnes CO2e)"]
    .sum()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Emissions (tonnes CO2e)"})
    .sort_values("Total Emissions (tonnes CO2e)", ascending=False)
)

mb_2005_csv = os.path.join(OUT_DIR, "mb_emissions_by_facility_2005.csv")
manitoba_emissions_2005.to_csv(mb_2005_csv, index=False)
print(f"Saved MB emissions by facility (2005) → {mb_2005_csv}")

plt.figure(figsize=(10, 6))
plt.barh(manitoba_emissions_2005["Facility Description"], manitoba_emissions_2005["Total Emissions (tonnes CO2e)"], color="skyblue")
plt.xlabel("Total Emissions (tonnes CO2e)")
plt.title("Manitoba Emissions by Facility (2005)")
plt.gca().invert_yaxis()
plt.tight_layout()
mb_2005_png = os.path.join(OUT_DIR, "mb_emissions_by_facility_2005.png")
plt.savefig(mb_2005_png, dpi=200)
plt.show()

# =========================================================================================
# Part 3: Top 10 Facility Descriptions by emissions in 2023 — Spark limit(10) equivalent
# =========================================================================================
mb_2023 = manitoba_overall_df[manitoba_overall_df["Reference Year"] == 2023]
manitoba_emissions_2023 = (
    mb_2023.groupby("Facility Description", as_index=False)["Total Emissions (tonnes CO2e)"]
    .sum()
    .rename(columns={"Total Emissions (tonnes CO2e)": "Total Emissions (tonnes CO2e)"})
    .sort_values("Total Emissions (tonnes CO2e)", ascending=False)
    .head(10)
)

mb_2023_csv = os.path.join(OUT_DIR, "mb_top10_emissions_by_facility_2023.csv")
manitoba_emissions_2023.to_csv(mb_2023_csv, index=False)
print(f"Saved MB top-10 facilities by emissions (2023) → {mb_2023_csv}")

plt.figure(figsize=(12, 6))
plt.bar(manitoba_emissions_2023["Facility Description"],
        manitoba_emissions_2023["Total Emissions (tonnes CO2e)"],
        color="skyblue")
plt.xlabel("Facility Description")
plt.ylabel("Total Emissions (tonnes CO2e)")
plt.title("Manitoba — Top 10 Facilities by Total Emissions (2023)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
mb_2023_png = os.path.join(OUT_DIR, "mb_top10_emissions_by_facility_2023.png")
plt.savefig(mb_2023_png, dpi=200)
plt.show()

# ==========================================================
# Part 4: Simple projections (2023→2027) with 16% YoY drop
# ==========================================================
years = [2023, 2024, 2025, 2026, 2027]

# Get last known total for 2023 from the by-year table
row_2023 = manitoba_emissions_sum_df.loc[
    manitoba_emissions_sum_df["Reference Year"] == 2023
]
if not row_2023.empty:
    last_known_sum = float(row_2023["Total Emissions (tonnes CO2e) (sum)"].values[0])

    # Build prediction series: include 2023, then apply 0.84 factor each year
    preds = [(2023, last_known_sum)]
    current = last_known_sum
    for year in years[1:]:
        current *= 0.84  # 16% reduction
        preds.append((year, current))

    # Convert to DataFrame
    predictions_df = pd.DataFrame(
        preds, columns=["Reference Year", "Predicted Total Emissions (tonnes CO2e)"]
    )

    # Save predictions and their total
    mb_preds_csv = os.path.join(OUT_DIR, "mb_predictions_2023_2027.csv")
    predictions_df.to_csv(mb_preds_csv, index=False)
    print(f"Saved MB predictions (2023–2027) → {mb_preds_csv}")

    total_predicted_emissions = predictions_df["Predicted Total Emissions (tonnes CO2e)"].sum()
    mb_preds_sum_txt = os.path.join(OUT_DIR, "mb_predictions_total_2023_2027.txt")
    with open(mb_preds_sum_txt, "w") as f:
        f.write(str(total_predicted_emissions))
    print(f"Saved total of predicted emissions → {mb_preds_sum_txt}")

    # Plot predictions
    plt.figure(figsize=(10, 6))
    plt.plot(
        predictions_df["Reference Year"],
        predictions_df["Predicted Total Emissions (tonnes CO2e)"],
        marker="o"
    )
    plt.title("Manitoba — Predicted Total Emissions (16% YoY reduction)")
    plt.xlabel("Reference Year")
    plt.ylabel("Predicted Total Emissions (tonnes CO2e)")
    plt.grid(True)
    plt.xticks(predictions_df["Reference Year"])
    plt.tight_layout()
    mb_preds_png = os.path.join(OUT_DIR, "mb_predictions_2023_2027.png")
    plt.savefig(mb_preds_png, dpi=200)
    plt.show()
else:
    print("⚠️ 2023 not found in by-year table; skipping prediction step.")


