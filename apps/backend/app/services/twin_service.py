from app.services.dataset_service import get_sensor_readings
from app.services.permit_store import get_permits


def get_twin_state() -> dict:
    readings = get_sensor_readings()
    latest = readings[-1]
    permit = next(
        (item for item in get_permits() if item["status"].lower() == "active"),
        None,
    )
    methane = latest["value"]
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
        "sensor_history": readings,
        "data_source": "repository_dataset_snapshot",
        "data_notice": "Historical repository sample; not connected to live plant telemetry.",
    }
