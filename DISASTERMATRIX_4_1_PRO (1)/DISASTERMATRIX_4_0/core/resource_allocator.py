def allocate_resources(zones, total_teams, total_vehicles, total_kits):
    """Greedy proportional allocation with deterministic largest-remainder distribution."""
    if min(total_teams, total_vehicles, total_kits) < 0:
        raise ValueError("Resource counts cannot be negative.")
    ranked = []
    for z in zones:
        priority = max(0.0, float(z.get("priority", 1))) * max(0.0, float(z.get("affected", 0)))
        ranked.append((z.get("zone","Unknown"), priority))
    denom = sum(p for _,p in ranked)
    result = []
    for name, priority in ranked:
        share = priority / denom if denom else 0
        result.append({"zone":name, "priority_score":round(priority,2),
                       "teams":int(total_teams*share), "vehicles":int(total_vehicles*share),
                       "kits":int(total_kits*share)})
    # Allocate remaining units to highest priority zones without exceeding totals.
    for key,total in (("teams",total_teams),("vehicles",total_vehicles),("kits",total_kits)):
        remaining = total - sum(r[key] for r in result)
        order = sorted(range(len(result)), key=lambda i: result[i]["priority_score"], reverse=True)
        for i in order[:remaining]:
            result[i][key] += 1
    return result
