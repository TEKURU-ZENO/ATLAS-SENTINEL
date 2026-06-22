def forecast_incident(state: dict) -> dict:
    risk = state.get("risk_score", 0)
    state["forecast"] = {
        "now": risk,
        "in_30_min": min(risk + 8, 99),
        "in_60_min": min(risk + 11, 99),
    }
    return state
