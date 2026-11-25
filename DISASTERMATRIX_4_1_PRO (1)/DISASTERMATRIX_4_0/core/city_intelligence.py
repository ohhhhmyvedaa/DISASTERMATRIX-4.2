from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CITY_COORDINATES = {
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "label": "City-centre reference"},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083, "label": "City-centre reference"},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "label": "City-centre reference"},
}

def load_hazard_sources():
    return pd.read_csv(DATA_DIR / "city_hazard_sources.csv")

def load_chennai_locations():
    return pd.read_csv(DATA_DIR / "chennai_gcc_drainage_intervention_locations.csv")

def city_summary(city):
    if city == "Chennai":
        return {
            "headline": "15 zones · 200 wards",
            "detail": "The GCC 2026 City Disaster Management Plan directory documents 15 administrative zones and ward ranges 1–200. GCC Resolution 089/2021 lists 90 roads across 23 locations for missing-link storm-water-drain works identified after the 2020 monsoon.",
            "caveat": "The drainage-intervention register is a historical planning record, not proof that a street is flooded today.",
        }
    if city == "Puducherry":
        return {
            "headline": "Official regional flood-hazard map available",
            "detail": "The Government of India/NCDC Puducherry climate-health action plan includes a modelled flood-hazard map with four depth classes: below 1 m, 1–2 m, 2–3 m and above 3 m. It identifies Oulgaret and Puducherry municipalities as flood-prone in its regional assessment.",
            "caveat": "These are regional modelled hazard classes from the cited plan, not current water depths or street-level live warnings.",
        }
    return {
        "headline": "City flood-vulnerability assessment published",
        "detail": "The Tiruchirappalli City Corporation climate-resilient action plan describes a 2023 flood-inundation assessment, reports 73 water-logged/flood points mapped spatially, and identifies wards 28 and parts of wards 2, 27, 21, 17, 31, 33, 53, 52 and 30 among the critical ward references.",
        "caveat": "The report's estimated 21% city influence area and 0.23 million affected population are planning-assessment figures, not a current event measurement.",
    }
