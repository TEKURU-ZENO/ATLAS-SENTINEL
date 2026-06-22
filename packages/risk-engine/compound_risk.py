def compound_risk_score(state: dict) -> int:
    score = 18
    score += 25 if state.get("methane_percent_lel", 0) >= 2.5 else 0
    score += 20 if state.get("active_hot_work") else 0
    score += 12 if state.get("maintenance_active") else 0
    score += 11 if state.get("shift_handover") else 0
    return min(score, 99)
