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
Each script can be run standalone (example below) and plots/tables are saved to outputs/"Province Name"/
```bash
python src/phase1_ingestion_cleaning.py
```

## 🧭 Provincial Insights & Recommendations

### British Columbia (BC)
Insights:
- Consistently ~5–6% of Canada’s total emissions, but proportionally more significant in recent years.
- Industrial manufacturing and energy transmission dominate emissions.

Recommendations:
- Invest in clean industrial technologies (e.g., CCS in aluminum/cement).
- Electrify energy infrastructure using hydro resources.
- Support green innovation hubs for sustainable industry.

### Alberta
Insights:
- Major targets: 45% reduction in methane emissions from 2014 levels by 2025 and cap oil sands–related emissions under 100 Mt CO₂e annually.
- Oil sands and methane dominate the carbon profile.

Recommendations:
- Scale methane leak detection and capture.
- Deploy CCUS in oil sands operations.
- Incentivize lower-carbon extraction and refining.

### Manitoba
Insights:
- Smaller absolute emitter compared to western provinces.
- Hydro power and efficiency already contribute strongly.

Recommendations:
- Expand electrification of transport & heating with hydro.
- Promote building retrofits for energy efficiency.
- Explore interprovincial electricity exports to displace fossil fuels elsewhere.

### New Brunswick
Insights:
- On track to meet/exceed 2030 and 2050 targets; emissions declining since 2005.
- 2005 drop linked to fossil plant retrofit.
- Fossil power and petroleum refineries are top emitters.

Recommendations:
- Set more ambitious post-2050 targets.
- Tighten standards for petroleum refineries.
- Expand wind generation leveraging NB’s strong wind resource.

### Nova Scotia
Insights:
- Historically fossil power dominated (~10 Mt annually) until decline post-2010.
- Petroleum refineries emit ~2 Mt annually; improvements after 2014.
- Other sectors contribute less.

Recommendations:
- Scale wind generation (abundant potential).
- Import hydro from Quebec to reduce coal reliance.
- Modernize grid to cut transmission losses.

### Ontario
Insights:
- Emissions dominated by industry (steel, cement, heavy sectors) plus transportation.
- Coal phase-out drove past reductions, but recent upticks threaten 2030/2050 alignment.

Recommendations:
- Expand EV adoption and charging infrastructure.
- Decarbonize industry through electrification + CCS.
- Maintain low-carbon grid with nuclear & renewables.

### Prince Edward Island (PEI)
Insights:
- Small absolute emitter due to size.
- Agriculture and transport dominate emissions.

Recommendations:
- Incentivize EVs and public transport electrification.
- Support low-carbon farming practices (methane capture, precision ag).
- Invest in small-scale wind and solar to reduce import reliance.

### Quebec
Insights:
- Abundant hydro keeps electricity emissions low.
- Industry (aluminum, cement, chemicals) is key emitter.

Recommendations:
- Electrify industrial processes using hydro.
- Support low-carbon material innovation.
- Boost EV adoption leveraging renewable power.

### Saskatchewan
Insights:
- High emissions from fossil power reliance.
- Target: 30% below 2005 by 2030.

Recommendations:
- Transition coal plants to gas, biomass, or renewables.
- Scale CCUS (expand Boundary Dam model).
- Invest in wind/solar to diversify.

### Newfoundland & Labrador
Insights:
- Offshore oil extraction is dominant.
- Smaller industrial base but high intensity in facilities.

Recommendations:
- Tighten methane monitoring offshore.
- Expand renewables (wind, hydro).
- Explore hydrogen production from surplus renewable energy.
