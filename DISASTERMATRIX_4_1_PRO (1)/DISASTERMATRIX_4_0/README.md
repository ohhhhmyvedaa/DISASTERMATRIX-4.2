# DISASTERMATRIX 4.0
### The Mathematical Brain of a Disaster-Resilient City

A modular educational disaster-management laboratory combining Arduino sensor telemetry, transparent flood mathematics, city risk comparison, route optimisation, historical climate references, simulations, experiment logging and an AI project companion.

> **Safety and scientific integrity:** This is an educational prototype. It is not an official flood forecast, public warning service, surveyed GIS system or certified emergency-response tool. Never use its route or resource suggestions for real emergencies. Follow official authorities.

## 1. What is included

- Professional Streamlit command-centre interface.
- Three city profiles: Chennai, Puducherry and Tiruchirappalli.
- Historical rainfall reference values transcribed from government publications (see `data/city_historical_rainfall.csv`).
- Optional external weather context through Open-Meteo. This is third-party model/API information, not an official gauge or the Arduino sensor.
- Arduino JSON serial protocol and configurable COM port.
- HC-SR04 water-depth conversion, capacitive soil-moisture calibration and secondary water-contact input.
- Rectangular tank volume, rainfall volume, water balance, rate of rise and transparent weighted risk index.
- 4×4 educational city grid, NetworkX/Dijkstra route demonstration and resource allocation.
- Flood, drainage, saturation, cyclone, wildfire and vibration teaching simulations.
- Conventional-vs-optimised model comparison.
- SQLite experiment history, CSV export and PDF report.
- AI companion with offline knowledge answers and optional OpenAI API integration.

## 2. Architecture

`app.py` is the UI entry point. The `core/` package contains independently testable calculations and integrations. `ai/` contains a local project assistant and optional online LLM adapter. `data/` contains curated historical reference data and SQLite is created automatically at runtime.

## 3. Historical city data and provenance

The included CSV is a small, traceable reference table, not a complete daily time series.

- **Chennai:** Tamil Nadu Climate Action Plan reports average annual rainfall of 1,298 mm for 1970–2000 and about 2,830 mm in 2021.
- **Puducherry:** Puducherry District Disaster Management Action Plan 2023 lists annual rainfall of 2,561.6 mm in 2021 and 1,267 mm in 2022.
- **Tiruchirappalli:** Trichy Climate Resilient City Action Plan reports 860.3 mm average annual rainfall over 1901–2023 and 761 mm in 2023. A separate district industry profile provides 2014–2018 monthly/year totals.

Source URLs:
1. Chennai Climate Action Plan: https://tngcc.tn.gov.in/wp-content/uploads/2025/10/Chennai_Climate_Action_Plan_ENG_5d827c7dec_compressed.pdf
2. Puducherry District Disaster Management Action Plan 2023: https://revenue.py.gov.in/downloads/dm/DM%20Action%20Plan%202023.pdf
3. Trichy Climate Resilient City Action Plan: https://www.trichycorporation.gov.in/wh-assets/tccdetails/CAP.pdf
4. Trichy district rainfall profile: https://msmedi-chennai.gov.in/GARMS_Admin/basictools/images/DIPSReport/Trichy.pdf

These values use different periods and geographic definitions (city/district/region). Do not directly rank cities from unlike periods. The app displays the period and source beside each value.

## 4. Windows installation

Install Python 3.10 or later. Open PowerShell in this folder:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The app starts without Arduino. Select **Simulation / Manual** mode. For live serial, connect the board and choose its COM port under **Hardware & Calibration**.

## 5. Arduino wiring (verify module-specific pinouts)

| Component | Arduino connection |
|---|---|
| HC-SR04 TRIG | D8 |
| HC-SR04 ECHO | D9 |
| Capacitive soil sensor AO | A0 |
| Secondary water module DO | D2 |
| I2C LCD SDA | A4 (Uno) |
| I2C LCD SCL | A5 (Uno) |
| Buzzer control | D6 |
| MOSFET driver signal | D5 |

- LCD I2C address defaults to `0x27`; some modules use `0x3F`.
- Secondary water sensor defaults to digital output. Confirm whether your module has active-HIGH or active-LOW output before connecting.
- Power pump from a separate correctly rated low-voltage supply through a suitable MOSFET driver. Join grounds as required by the driver design. Never power a pump from an Arduino GPIO.
- Use a suitable flyback protection arrangement for an inductive pump if not already integrated into the driver.
- Do not connect a 5V echo directly to a 3.3V-only board. This project targets Arduino Uno R3.
- Test the pump with adult/teacher supervision and keep water away from the laptop and mains wiring.

## 6. HC-SR04 calibration

Measure the fixed vertical distance from the sensor face to the tank bottom when empty. Enter this as `reference_height_cm`.

`water_depth_cm = reference_height_cm - measured_distance_cm`

Clamp only small negative readings to zero if appropriate; reject distances outside the calibrated tank range. The ultrasonic sensor measures distance to the water surface, not depth directly.

For the soil sensor, record ADC readings in representative dry and wet soil. Enter the two calibration endpoints. The percentage is a relative experimental scale, not laboratory volumetric water content.

## 7. Mathematics

- Tank volume (litres): `length_cm × width_cm × depth_cm / 1000`.
- Rainfall volume (litres): `rain_mm × collection_area_m2` because 1 mm over 1 m² equals 1 litre.
- Water balance: `Δstorage = inflow − drainage − infiltration`.
- Rate of rise: `(current_depth − previous_depth) / elapsed_minutes`.
- Experimental risk index: weighted normalised components from depth, rise rate, soil moisture and drainage stress. It is an index, not probability.
- MAE: mean absolute difference between predicted and later observed water levels.

## 8. Serial protocol

Arduino sends one newline-terminated JSON object per update:

```json
{"water_level_cm":5.4,"distance_cm":14.6,"soil_moisture_pct":42.0,"water_sensor":1,"pump_status":0,"buzzer_status":0,"valid":true}
```

Missing or invalid readings must be `null` or `valid:false`, never silently converted to zero. The Python serial handler validates the fields and timestamp on receipt.

## 9. AI companion

The built-in offline assistant answers common project and mathematics questions. For richer generative answers, copy `.env.example` to `.env`, add your own API key and install the optional OpenAI package (already listed in requirements). Never commit `.env`. API use may incur charges and requires internet access. The AI is an explainer, not a sensor authority or emergency decision-maker.

## 10. Run tests

```powershell
python -m unittest discover -s tests -v
```

## 11. Limitations

- Historical data are curated reference points, not a harmonised multi-city daily dataset.
- The optional weather endpoint may be unavailable and may provide modelled weather rather than station observations.
- The 4×4 city grid and routes are illustrative, not actual streets, elevations or shelters.
- The Arduino tank model does not measure rainfall. Rainfall is manual or simulated.
- Prediction is a simple trend estimate and is not validated flood forecasting.
- Pump output logic is a classroom demonstration and must be checked against the real pump, driver, supply and plumbing before use.


## 12. City Hazard Atlas (research upgrade)

The **City Hazard Atlas** page uses documented official planning material rather than invented street-level risk coordinates:

- **Chennai:** GCC City Disaster Management Perspective Plan 2026 directory documents 15 zones and ward ranges 1–200. GCC Resolution 089/2021 documents a missing-link storm-water-drain programme list covering 90 roads across 23 locations. The project includes a selected subset of street/zone/division entries in `data/chennai_gcc_drainage_intervention_locations.csv`; it is not the complete 90-road list and is not a live flood report.
- **Puducherry:** The Government of India/NCDC State Action Plan for Climate Change & Human Health includes a regional modelled flood-hazard map with classes below 1 m, 1–2 m, 2–3 m and above 3 m. It notes Oulgaret and Puducherry municipalities in the regional flood-prone discussion.
- **Tiruchirappalli:** The 2024 City Corporation climate-resilient action plan contains a 2023 flood-inundation map and discusses mapped water-logging/flood points, vulnerable wards and a city-level flood influence estimate. The project reports these as planning-study findings, not live conditions.

The map markers are **city-centre locator points only**. No ward polygon, street coordinate, shelter coordinate or flood extent is fabricated. Use official source links in the app to inspect original map PDFs.

### Official data portals
- IMD API reference: https://api.imd.gov.in/public/api_reference.html
- NWIC daily IMD rainfall: https://nwdp.nwic.gov.in/en/dataset/rainfall-daily-imd
- data.gov.in rainfall catalogue: https://data.gov.in/catalog/rainfall
- Tiruchirappalli District Disaster Management 2026 portal: https://tiruchirappalli.nic.in/disaster-management/

Official IMD API access may require registration and credentials. Do not describe an endpoint as connected until credentials and returned data have been tested.
