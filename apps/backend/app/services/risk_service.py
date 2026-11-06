from app.services.twin_service import get_twin_state
from app.services.risk_model import compound_risk


def get_current_risk() -> dict:
    twin = get_twin_state()
    model = compound_risk(twin)
    risk = model["score"]
    history = twin.get("sensor_history", [])
    latest = history[-1] if history else None
    previous = history[-2] if len(history) > 1 else None
    delta = twin["methane_percent_lel"] - previous["value"] if previous and twin["methane_percent_lel"] is not None else None
    sensor_trend = "unknown" if delta is None else "rising" if delta > 0 else "falling" if delta < 0 else "stable"
    leading_interactions = ", ".join(item["label"].lower() for item in model["interactions"][:2]) or "the available sensor and permit signals"
    has_sample = bool(history)
    current_score = min(risk, 99) if has_sample and not twin["sensor_stale"] and twin["sensor_verified"] else None
    status = "available" if current_score is not None else "unavailable" if not has_sample else "stale" if twin["sensor_stale"] else "unverified"
    reason = "Current risk is unavailable because no sensor sample is available." if not has_sample else (
        f"Current risk is unavailable because the latest sensor sample is stale; the last recorded sample scored {risk}/99."
        if twin["sensor_stale"] else f"Current risk is unavailable because the sensor source is not verified; the sample scored {risk}/99."
        if not twin["sensor_verified"] else f"Risk is elevated by {leading_interactions}. This is a current-state score, not an incident forecast."
    )
    return {
        "current": current_score,
        "snapshot_score": min(risk, 99) if current_score is None and has_sample else None,
        "status": status,
        "sensor_trend": sensor_trend,
        "sensor_delta": round(delta, 3) if delta is not None else None,
        "reason": reason,
        "level": model["level"] if current_score is not None else "unknown",
        "drivers": model["drivers"] if current_score is not None else [],
        "interactions": model["interactions"] if current_score is not None else [],
        "snapshot_drivers": model["drivers"] if current_score is None and has_sample else [],
        "snapshot_interactions": model["interactions"] if current_score is None and has_sample else [],
        "method": model["method"],
        "sensor_timestamp": twin["sensor_timestamp"],
        "trend_timestamp": latest["timestamp"] if latest else None,
        "sensor_stale": twin["sensor_stale"],
        "sensor_verified": twin["sensor_verified"],
        "sensor_age_minutes": twin["sensor_age_minutes"],
        "data_source": twin["data_source"],
        "data_notice": twin["data_notice"],
    }
