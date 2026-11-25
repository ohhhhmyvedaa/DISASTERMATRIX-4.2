def simulate(scenario, rainfall_mm=60, drainage_efficiency=0.6, soil_saturation=70,
             starting_depth_cm=4, duration_min=30):
    """Illustrative lumped model. Output is simulated, not a forecast."""
    intensity_factor={"Urban flooding":1.0,"Heavy rainfall":1.35,"Drainage blockage":1.25,
                      "Soil saturation":1.15,"Earthquake vibration demo":0.15,
                      "Cyclone scenario":1.3,"Wildfire scenario":0.05}.get(scenario,1.0)
    infiltration_factor=max(0.05,1-soil_saturation/120)
    effective_rain=rainfall_mm*intensity_factor
    runoff=effective_rain*(1-infiltration_factor*0.45)
    drainage=max(0,drainage_efficiency)*effective_rain*0.55
    delta_cm=max(0,(runoff-drainage)*0.08)
    end_depth=starting_depth_cm+delta_cm
    return {"scenario":scenario,"rainfall_input_mm":rainfall_mm,"effective_runoff_mm":round(runoff,2),
            "drainage_equivalent_mm":round(drainage,2),"start_depth_cm":starting_depth_cm,
            "end_depth_cm":round(end_depth,2),"delta_depth_cm":round(delta_cm,2),
            "duration_min":duration_min,"label":"SIMULATED — educational model only"}
