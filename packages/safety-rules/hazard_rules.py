def is_compound_hazard(state: dict) -> bool:
    return bool(state.get("active_hot_work") and state.get("maintenance_active") and state.get("methane_percent_lel", 0) >= 2.5)
