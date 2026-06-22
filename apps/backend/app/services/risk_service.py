from app.services.twin_service import get_twin_state


def get_current_risk() -> dict:
    twin = get_twin_state()
    risk = 18
    if twin["methane_percent_lel"] >= 2.5:
        risk += 25
    if twin["active_hot_work"]:
        risk += 20
    if twin["maintenance_active"]:
        risk += 12
    if twin["shift_handover"]:
        risk += 11
    return {
        "current": min(risk, 99),
        "forecast30": min(risk + 8, 99),
        "forecast60": min(risk + 11, 99),
        "reason": "Gas rise overlaps with hot work, maintenance, and shift handover.",
    }
