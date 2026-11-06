import os
import sys
from pathlib import Path

from app.services.permit_store import audit_log, get_permits, suspend
from app.services.twin_service import get_twin_state


RULES_PATH = Path(__file__).resolve().parents[4] / "packages" / "safety-rules"
if str(RULES_PATH) not in sys.path:
    sys.path.insert(0, str(RULES_PATH))
from permit_rules import evaluate_permit  # noqa: E402


def evaluate_all_permits(execute_suspensions: bool = False) -> dict:
    current = get_twin_state()
    evaluated = []
    for permit in get_permits():
        if permit["status"] not in {"active", "open"}:
            evaluated.append({"permit_id": permit["permit_id"], "zone": permit["zone"], "decision": "no_change", "findings": [], "rules": []})
            continue
        has_fresh_sensor = permit["zone"] == current["zone"] and not current["sensor_stale"] and current["sensor_verified"]
        state = current if has_fresh_sensor else {"methane_percent_lel": None}
        evaluated.append(evaluate_permit(permit, state))

    changed = []
    if execute_suspensions:
        if os.getenv("ATLAS_ENABLE_PERMIT_ACTIONS", "false").lower() != "true":
            raise PermissionError("Permit actions are disabled. Set ATLAS_ENABLE_PERMIT_ACTIONS=true to enable the local audited permit mirror.")
        changed = suspend(evaluated)
    return {
        "evaluations": evaluated,
        "suspended": changed,
        "executed": bool(execute_suspensions),
        "audit": audit_log(),
        "notice": "Actions update the local audited demo permit mirror only; no external permit system or plant control is connected. Sensor-dependent checks hold when matching data is missing, stale, or unverified.",
    }


def validate_permits() -> dict:
    result = evaluate_all_permits()
    active = next((item for item in result["evaluations"] if item["decision"] != "no_change"), None)
    current = get_twin_state()
    return {
        "permit": active["permit_id"] if active else current["permit_id"],
        "zone": current["zone"],
        "equipment": current["equipment"],
        "sensor_reading_percent_lel": current["methane_percent_lel"],
        "sensor_timestamp": current["sensor_timestamp"],
        "sensor_stale": current["sensor_stale"],
        "sensor_verified": current["sensor_verified"],
        "sensor_age_minutes": current["sensor_age_minutes"],
        "valid": not active or active["decision"] == "continue",
        "decision": active["decision"] if active else "no_active_permit",
        "evidence": active["findings"] if active else [],
        "evaluations": result["evaluations"],
        "notice": result["notice"],
    }
