def hot_work_gas_violation(state: dict) -> bool:
    return state.get("active_hot_work") and state.get("methane_percent_lel", 0) >= 2.5
