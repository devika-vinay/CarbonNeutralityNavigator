# Carbon Neutrality Navigator

## ⚠️ Problem Statement
Despite the extensive greenhouse gas emissions data provided by the federal website, a critical gap remains in understanding how provincial emission reduction commitments align with Canada’s overarching goal of achieving carbon neutrality by 2050. The analysis aims to:

1. Evaluate Provincial Commitments: Assess each province's targets to understand the diversity and ambition of regional strategies.

2. Correlate Trends with Federal Goals: Compare historical emissions trends from the dataset with the provincial benchmarks, determining how current progress aligns with the federal mandate for carbon neutrality.

3. Identify Opportunities for Intervention: Highlight gaps, successes, and potential areas for policy and business interventions to better align provincial efforts with the national carbon neutrality target.

By bridging provincial benchmarks with emission trend data, this project aims to deliver actionable, data-driven insights that can inform policymakers and industry leaders in refining strategies to meet Canada’s 2050 carbon neutrality goal.

## 📦 Data
CSVs read from `data/`:
- `GHGEmissions.csv` – facility-level emissions across country
- `ProvincialTargets.csv` – provincial targets 

## 🛠️ Environment
- Python 3.11+
- `pip install -r requirements.txt` 

## ▶️ How to run
Each script can be run standalone, eg:
```bash
python src/phase1_ingestion_cleaning.py
