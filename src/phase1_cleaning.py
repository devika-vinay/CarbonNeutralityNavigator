import pandas as pd
import os

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

############################################################################################################################
# DATASET 1
############################################################################################################################

# Load the CSV file from data folder
emission_df = pd.read_csv("data/GHGEmissions.csv")

# Dropping columns unnecessary for analysis
columns_to_drop = [
    "GHGRP ID No. / No d'identification du PDGES",
    "Facility Location / Emplacement de l'installation",
    "Facility City or District or Municipality / Ville ou District ou Municipalité de l'installation",
    "Latitude",
    "Longitude",
    "Facility Postal Code / Code postal de l'installation",
    "Facility NPRI ID / Numéro d'identification de l'INRP",
    "Facility NAICS Code / Code SCIAN de l'installation",
    "French Facility NAICS Code Description / Description du code SCIAN de l'installation en français",
    "Reporting Company Legal Name / Dénomination sociale de la société déclarante",
    "Reporting Company Business Number / Numéro d'entreprise de la société déclarante",
    "DUNS Number / Numéro DUNS",
    "Public Contact Name / Nom du responsable des renseignements au public",
    "Public Contact Position / Poste ou Titre du responsable des renseignements au public",
    "Public Contact Telephone / Numéro de téléphone du responsable des renseignements au public",
    "Public Contact Extension / Poste téléphonique du responsable des renseignements au public",
    "Public Contact Email / Adresse électronique du responsable des renseignements au public",
    "Public Contact Mailing Address / Adresse postale du responsable des renseignements au public",
    "Public Contact City or District or Municipality / Ville ou District ou Municipalité du responsable des renseignements au public",
    "Public Contact Province or Territory / Province ou Territoire du responsable des renseignements au public",
    "Public Contact Postal Code / Code postal du responsable des renseignement au public",
    "GHGRP Quantification Requirements / Exigences de quantification du PDGES",
    "Emission Factors / Coefficients d'émission",
    "Engineering Estimates / Estimations techniques",
    "Mass Balance / Bilan massique",
    "Monitoring or Direct Measurement / Surveillance ou mesure directe",
]

emission_df.drop(columns=columns_to_drop, inplace=True)

# Renaming columns to remove french labels
columns_rename_map = {
    "Reference Year / Année de référence": "Reference Year",
    "Facility Name / Nom de l'installation": "Facility Name",
    "Facility City or District or Municipality / Ville ou District ou Municipalité de l'installation": "Facility City",
    "Facility Province or Territory / Province ou territoire de l'installation": "Facility Province",
    "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais": "Facility Description",
    "Reporting Company Trade Name / Nom commercial de la société déclarante": "Reporting Company",
    "CH4 (tonnes CO2e / tonnes éq. CO2)": "CH4 (tonnes CO2e)",
    "N2O (tonnes CO2e / tonnes éq. CO2)": "N2O (tonnes CO2e)",
    "HFC-23 (tonnes CO2e / tonnes éq. CO2)": "HFC-23 (tonnes CO2e)",
    "HFC-32 (tonnes CO2e / tonnes éq. CO2)": "HFC-32 (tonnes CO2e)",
    "HFC-41 (tonnes CO2e / tonnes éq. CO2)": "HFC-41 (tonnes CO2e)",
    "HFC-43-10mee (tonnes CO2e / tonnes éq. CO2)": "HFC-43-10mee (tonnes CO2e)",
    "HFC-125 (tonnes CO2e / tonnes éq. CO2)": "HFC-125 (tonnes CO2e)",
    "HFC-134 (tonnes CO2e / tonnes éq. CO2)": "HFC-134 (tonnes CO2e)",
    "HFC-134a (tonnes CO2e / tonnes éq. CO2)": "HFC-134a (tonnes CO2e)",
    "HFC-143 (tonnes CO2e / tonnes éq. CO2)": "HFC-143 (tonnes CO2e)",
    "HFC-143a (tonnes CO2e / tonnes éq. CO2)": "HFC-143a (tonnes CO2e)",
    "HFC-152a (tonnes CO2e / tonnes éq. CO2)": "HFC-152a (tonnes CO2e)",
    "HFC-227ea (tonnes CO2e / tonnes éq. CO2)": "HFC-227ea (tonnes CO2e)",
    "HFC-236fa (tonnes CO2e / tonnes éq. CO2)": "HFC-236fa (tonnes CO2e)",
    "HFC-245ca (tonnes CO2e / tonnes éq. CO2)": "HFC-245ca (tonnes CO2e)",
    "HFC Total (tonnes CO2e / tonnes éq. CO2)": "HFC Total (tonnes CO2e)",
    "CF4 (tonnes CO2e / tonnes éq. CO2)": "CF4 (tonnes CO2e)",
    "C2F6 (tonnes CO2e / tonnes éq. CO2)": "C2F6 (tonnes CO2e)",
    "C3F8 (tonnes CO2e / tonnes éq. CO2)": "C3F8 (tonnes CO2e)",
    "C4F10 (tonnes CO2e / tonnes éq. CO2)": "C4F10 (tonnes CO2e)",
    "C4F8 (tonnes CO2e / tonnes éq. CO2)": "C4F8 (tonnes CO2e)",
    "C5F12 (tonnes CO2e / tonnes éq. CO2)": "C5F12 (tonnes CO2e)",
    "C6F14 (tonnes CO2e / tonnes éq. CO2)": "C6F14 (tonnes CO2e)",
    "PFC Total (tonnes CO2e / tonnes éq. CO2)": "PFC Total (tonnes CO2e)",
    "SF6 (tonnes CO2e / tonnes éq. CO2)": "SF6 (tonnes CO2e)",
    "Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)": "Total Emissions (tonnes CO2e)",
}

emission_df.rename(columns=columns_rename_map, inplace=True)

# Dropping columns as the CO2 equivalent of these gases have been provided
columns_to_drop_additional = [
    "CH4 (tonnes)",
    "N2O (tonnes)",
    "HFC-23 (tonnes)",
    "HFC-32 (tonnes)",
    "HFC-41 (tonnes)",
    "HFC-43-10mee (tonnes)",
    "HFC-125 (tonnes)",
    "HFC-134 (tonnes)",
    "HFC-134a (tonnes)",
    "HFC-143 (tonnes)",
    "HFC-143a (tonnes)",
    "HFC-152a (tonnes)",
    "HFC-227ea (tonnes)",
    "HFC-236fa (tonnes)",
    "HFC-245ca (tonnes)",
    "CF4 (tonnes)",
    "C2F6 (tonnes)",
    "C3F8 (tonnes)",
    "C4F10 (tonnes)",
    "C4F8 (tonnes)",
    "C5F12 (tonnes)",
    "C6F14 (tonnes)",
    "SF6 (tonnes)",
]

emission_df.drop(columns=columns_to_drop_additional, inplace=True)

# Drop individual gas emissions (keep totals)
columns_to_drop_gas = [
    "HFC-23 (tonnes CO2e)",
    "HFC-32 (tonnes CO2e)",
    "HFC-41 (tonnes CO2e)",
    "HFC-43-10mee (tonnes CO2e)",
    "HFC-125 (tonnes CO2e)",
    "HFC-134 (tonnes CO2e)",
    "HFC-134a (tonnes CO2e)",
    "HFC-143 (tonnes CO2e)",
    "HFC-143a (tonnes CO2e)",
    "HFC-152a (tonnes CO2e)",
    "HFC-227ea (tonnes CO2e)",
    "HFC-236fa (tonnes CO2e)",
    "HFC-245ca (tonnes CO2e)",
    "CF4 (tonnes CO2e)",
    "C2F6 (tonnes CO2e)",
    "C3F8 (tonnes CO2e)",
    "C4F10 (tonnes CO2e)",
    "C4F8 (tonnes CO2e)",
    "C5F12 (tonnes CO2e)",
    "C6F14 (tonnes CO2e)",
]

emission_df.drop(columns=columns_to_drop_gas, inplace=True)

# Impute missing values for reporting company
emission_df["Reporting Company"].fillna(emission_df["Facility Name"], inplace=True)

# Province fix for Fibrek SENC
emission_df["Facility Province"].fillna("Quebec", inplace=True)

# Save cleaned dataset
emission_df.to_csv("outputs/Cleaned_GHGEmissions.csv", index=False)

print("Cleaned GHG Emissions data saved to outputs/Cleaned_GHGEmissions.csv")

############################################################################################################################
# DATASET 2
############################################################################################################################

provincial_targets_df = pd.read_csv("data/ProvincialTargets.csv")
provincial_targets_df.fillna("N/A", inplace=True)

provincial_targets_df.to_csv("outputs/Cleaned_ProvincialTargets.csv", index=False)

print("Cleaned Provincial Targets data saved to outputs/Cleaned_ProvincialTargets.csv")
