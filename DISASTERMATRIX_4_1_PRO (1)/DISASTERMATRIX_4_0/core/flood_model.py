from dataclasses import dataclass

@dataclass
class Tank:
    length_cm: float = 40.0
    width_cm: float = 30.0
    reference_height_cm: float = 30.0

def water_depth(reference_height_cm: float, measured_distance_cm: float) -> float:
    if reference_height_cm <= 0 or measured_distance_cm < 0:
        raise ValueError("Tank height must be positive and distance cannot be negative.")
    depth = reference_height_cm - measured_distance_cm
    if depth < 0:
        raise ValueError("Distance exceeds reference height: check calibration.")
    if depth > reference_height_cm:
        raise ValueError("Depth exceeds tank reference height.")
    return float(depth)

def tank_volume_litres(length_cm: float, width_cm: float, depth_cm: float) -> float:
    if min(length_cm, width_cm, depth_cm) < 0:
        raise ValueError("Tank dimensions and depth cannot be negative.")
    return length_cm * width_cm * depth_cm / 1000.0

def rainfall_volume_litres(rainfall_mm: float, area_m2: float) -> float:
    if rainfall_mm < 0 or area_m2 < 0:
        raise ValueError("Rainfall and area cannot be negative.")
    return rainfall_mm * area_m2

def water_balance(inflow_l: float, drainage_l: float, infiltration_l: float) -> float:
    if min(inflow_l, drainage_l, infiltration_l) < 0:
        raise ValueError("Water balance terms cannot be negative.")
    return inflow_l - drainage_l - infiltration_l

def rate_of_rise(current_cm: float, previous_cm: float, elapsed_seconds: float):
    if elapsed_seconds <= 0:
        return None
    return (current_cm - previous_cm) / (elapsed_seconds / 60.0)

def linear_projection(readings, horizon_minutes=5):
    """Least-squares line over equally spaced recent samples; returns estimate or None."""
    values = [float(v) for v in readings if v is not None]
    if len(values) < 3:
        return None
    import numpy as np
    x = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(x, np.array(values), 1)
    return max(0.0, float(intercept + slope * (len(values)-1+horizon_minutes)))
