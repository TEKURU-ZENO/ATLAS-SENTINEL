def emergency_preparedness_required(state: dict) -> bool:
    return state.get("risk_score", 0) >= 80
