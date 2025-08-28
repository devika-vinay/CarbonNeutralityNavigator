# Carbon Neutrality Navigator
Actionable, province-level insights connecting federal facility-level GHG data to provincial targets to assess alignment with Canada’s 2050 carbon-neutrality objective. 

## 📦 Data
Place the required CSVs in `data/`:
- `emissions_facility_level.csv` – facility-level emissions across country
- `provincial_targets.csv` – provincial targets 

## 🛠️ Environment
- Python 3.11+
- `pip install -r requirements.txt` 

## ▶️ How to run
Each script can be run standalone:
```bash
python src/phase1_ingestion_cleaning.py
python src/phase2_bc.py
python src/phase3_ab_mb.py
python src/phase4_nb_ns.py
python src/phase5_on_pei.py
