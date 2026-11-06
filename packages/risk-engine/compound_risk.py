def compound_risk(state: dict) -> dict:
    gas = float(state.get("methane_percent_lel", 0))
    drivers = []
    if gas >= 1:
        drivers.append({"id": "methane", "label": "Combustible gas elevation", "points": min(30, round(gas * 4))})
    if state.get("active_hot_work"):
        drivers.append({"id": "hot_work", "label": "Active hot-work permit", "points": 15})
    if state.get("maintenance_active"):
        drivers.append({"id": "maintenance", "label": "Concurrent maintenance", "points": 10})
    if state.get("shift_handover"):
        drivers.append({"id": "handover", "label": "Shift handover window", "points": 8})
    active = {item["id"] for item in drivers}
    interactions = []
    pairs = [
        (("methane", "hot_work"), 18, "Gas with active ignition work"),
        (("methane", "maintenance"), 8, "Gas during maintenance activity"),
        (("hot_work", "handover"), 7, "Hot-work permit during handover"),
        (("maintenance", "handover"), 5, "Maintenance during handover"),
    ]
    for pair, points, label in pairs:
        if set(pair).issubset(active):
            interactions.append({"factors": list(pair), "label": label, "points": points})
    if {"methane", "hot_work", "handover"}.issubset(active):
        interactions.append({"factors": ["methane", "hot_work", "handover"], "label": "Three-way gas, ignition, and handover overlap", "points": 8})
    raw = 8 + sum(item["points"] for item in drivers) + sum(item["points"] for item in interactions)
    score = min(99, raw)
    return {
        "score": score,
        "raw_score": raw,
        "level": "critical" if score >= 80 else "high" if score >= 60 else "elevated" if score >= 35 else "low",
        "drivers": drivers,
        "interactions": interactions,
        "method": "ATLAS compound-risk v1: base + normalized driver points + explicit interaction premiums; capped at 99.",
    }


def compound_risk_score(state: dict) -> int:
    return compound_risk(state)["score"]
