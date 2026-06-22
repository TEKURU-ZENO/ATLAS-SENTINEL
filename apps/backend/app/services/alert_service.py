def build_alert() -> dict:
    return {
        "severity": "critical",
        "message": "Compound hazard detected in Zone C.",
        "notify": ["control_room", "field_safety", "emergency_response_team"],
    }
