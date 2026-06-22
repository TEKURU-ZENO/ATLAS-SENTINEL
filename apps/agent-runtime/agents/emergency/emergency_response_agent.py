def recommend_emergency_action(state: dict) -> dict:
    state["emergency_action"] = [
        "evacuate_zone_c",
        "suspend_hot_work_permit",
        "notify_emergency_response_team",
        "preserve_sensor_and_cctv_evidence",
    ]
    return state
