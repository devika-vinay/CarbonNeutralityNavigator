# Carbon Neutrality Navigator
Actionable, province-level insights connecting federal facility-level GHG data to provincial targets to assess alignment with Canada’s 2050 carbon-neutrality objective. 

## 📦 Data
Place the required CSVs in `data/`:
- `GHGEmissions.csv` – facility-level emissions across country
- `ProvincialTargets.csv` – provincial targets 

## 🛠️ Environment
- Python 3.11+
- `pip install -r requirements.txt` 

## ▶️ How to run
Each script can be run standalone, eg:
```bash
python src/phase1_ingestion_cleaning.py
