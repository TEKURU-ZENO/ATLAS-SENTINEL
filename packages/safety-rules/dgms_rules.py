def hazardous_area_exposure(state: dict) -> bool:
    return state.get("workers", 0) > 0 and state.get("risk_score", 0) >= 80
