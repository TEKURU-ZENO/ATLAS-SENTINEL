from app.services.twin_service import get_twin_state


def validate_permits() -> dict:
    twin = get_twin_state()
    blocked = twin["active_hot_work"] and twin["methane_percent_lel"] >= 2.5
    return {
        "permit": twin["permit_id"],
        "valid": not blocked,
        "decision": "suspend" if blocked else "continue",
        "evidence": "Hot work overlaps with elevated combustible gas.",
    }
