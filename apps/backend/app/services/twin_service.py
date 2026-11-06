import os
from datetime import datetime, timezone

from app.services.dataset_service import get_sensor_readings
from app.services.permit_store import get_permits


def get_twin_state() -> dict:
    try:
        readings = get_sensor_readings()
    except OSError:
        readings = []
    permits = get_permits()
    permit = next((item for item in permits if item["status"].lower() == "active"), None)
    if not readings:
        return {
            "zone": permit["zone"] if permit else "Unknown",
            "equipment": permit.get("equipment", "Unknown") if permit else "Unknown",
            "methane_percent_lel": None,
            "active_hot_work": bool(permit and permit["type"] == "hot_work"),
            "maintenance_active": None,
            "shift_handover": None,
            "workers": None,
            "permit_id": permit["permit_id"] if permit else None,
            "sensor_id": None,
            "sensor_timestamp": None,
            "sensor_age_minutes": None,
            "sensor_stale": True,
            "sensor_verified": False,
            "sensor_freshness_limit_minutes": max(0.0, float(os.getenv("ATLAS_SENSOR_MAX_AGE_MINUTES", "15"))),
            "sensor_history": [],
            "data_source": "sensor_unavailable",
            "data_notice": "No sensor sample is available. Current risk is unknown and sensor-dependent permit checks are held.",
        }
    latest = readings[-1]
    methane = latest["value"]
    max_age_minutes = max(0.0, float(os.getenv("ATLAS_SENSOR_MAX_AGE_MINUTES", "15")))
    try:
        observed_at = datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00"))
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - observed_at.astimezone(timezone.utc)).total_seconds() / 60
        sensor_stale = age_minutes < 0 or age_minutes > max_age_minutes
    except (TypeError, ValueError):
        age_minutes = None
        sensor_stale = True
    freshness_notice = (
        f" Latest sample age: {max(0, round(age_minutes))} minutes; freshness limit: {max_age_minutes:g} minutes."
        if age_minutes is not None and age_minutes >= 0
        else " Latest sample timestamp is invalid or in the future."
    )
    return {
        "zone": latest["zone"],
        "equipment": permit["equipment"] if permit else "Unknown",
        "methane_percent_lel": methane,
        "active_hot_work": bool(permit and permit["type"] == "hot_work"),
        "maintenance_active": None,
        "shift_handover": None,
        "workers": None,
        "permit_id": permit["permit_id"] if permit else None,
        "sensor_id": latest["sensor"],
        "sensor_timestamp": latest["timestamp"],
        "sensor_age_minutes": round(age_minutes, 1) if age_minutes is not None else None,
        "sensor_stale": sensor_stale,
        "sensor_verified": False,
        "sensor_freshness_limit_minutes": max_age_minutes,
        "sensor_history": readings,
        "data_source": "repository_demo_sample_unknown_provenance",
        "data_notice": "Illustrative repository sensor sample with unverified source and calibration; not verified telemetry and not connected to a live plant." + freshness_notice,
    }
