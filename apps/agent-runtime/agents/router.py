def route_next(state: dict) -> str:
    if state.get("risk_score", 0) >= 80:
        return "emergency_response_agent"
    if state.get("active_hot_work"):
        return "permit_intelligence_agent"
    return "hazard_correlation_agent"
