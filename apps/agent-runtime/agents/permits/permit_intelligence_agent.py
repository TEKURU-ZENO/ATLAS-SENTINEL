def evaluate_permit(state: dict) -> dict:
    violation = state.get("active_hot_work") and state.get("methane_percent_lel", 0) >= 2.5
    state["permit_decision"] = "suspend" if violation else "continue"
    return state
