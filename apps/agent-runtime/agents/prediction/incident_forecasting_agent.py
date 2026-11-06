def forecast_incident(state: dict) -> dict:
    """Rule-baseline trend projection; the learned model is evaluated separately."""
    risk = int(state.get("risk_score", 0))
    history = state.get("sensor_history", [])
    current_gas = state.get("methane_percent_lel")
    rising = len(history) > 1 and current_gas is not None and current_gas > history[-2].get("value", current_gas)
    increment = 10 if rising else 3
    state["forecast"] = {
        "now": risk,
        "in_30_min": min(99, risk + increment),
        "in_60_min": min(99, risk + increment + (10 if rising else 4)),
        "method": "compound-rule score plus recent sensor trend; not the trained classifier",
    }
    return state
