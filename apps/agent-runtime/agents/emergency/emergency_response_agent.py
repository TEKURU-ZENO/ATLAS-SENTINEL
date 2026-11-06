def recommend_emergency_action(state: dict) -> dict:
    zone = state.get("zone", "the affected zone")
    permit_id = state.get("permit_id")
    actions = [f"stop ignition work in {zone}", "verify atmosphere with calibrated site instrumentation", "notify the site control room"]
    if permit_id:
        actions.insert(1, f"request authorized suspension review for {permit_id}")
    state["emergency_recommendation"] = {
        "zone": zone,
        "actions": actions,
        "requires_authorized_site_response": True,
        "external_actions_executed": False,
    }
    return state
