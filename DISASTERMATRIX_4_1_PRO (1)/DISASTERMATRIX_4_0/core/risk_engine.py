def clamp(value, low=0.0, high=100.0):
    return max(low, min(high, float(value)))

def weighted_risk(depth_pct, rise_pct, soil_pct, drainage_stress_pct,
                  weights=(0.40, 0.30, 0.15, 0.15)):
    values = [clamp(v) for v in (depth_pct, rise_pct, soil_pct, drainage_stress_pct)]
    if len(weights) != 4 or any(w < 0 for w in weights):
        raise ValueError("Four non-negative weights are required.")
    total = sum(weights)
    if total <= 0:
        raise ValueError("At least one risk weight must be positive.")
    norm = [w / total for w in weights]
    score = sum(v*w for v, w in zip(values, norm))
    return round(score, 2)

def risk_label(score):
    if score < 25: return "LOW"
    if score < 50: return "MODERATE"
    if score < 75: return "HIGH"
    return "CRITICAL"
