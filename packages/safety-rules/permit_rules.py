from datetime import datetime, timezone


# Prototype assumption only; this threshold is not asserted as a regulatory clause.
HOT_WORK_GAS_HOLD_PERCENT_LEL = 2.5


def evaluate_permit(permit: dict, state: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    status = str(permit.get("status", "")).lower()
    findings = []
    if status not in {"active", "open"}:
        return {"permit_id": permit.get("permit_id", permit.get("id")), "decision": "no_change", "rules": [], "findings": []}

    reading = state.get("methane_percent_lel")
    if reading is None:
        findings.append({"rule_id": "SENSOR-001", "severity": "hold", "reason": "No current zone sensor reading is available."})
    elif permit.get("type", "").lower() == "hot_work" and float(reading) >= HOT_WORK_GAS_HOLD_PERCENT_LEL:
        findings.append({
            "rule_id": "HOTWORK-GAS-001",
            "severity": "suspend",
            "reason": f"Hot work overlaps with {float(reading):.2f}% LEL; configured demo hold threshold is {HOT_WORK_GAS_HOLD_PERCENT_LEL:.1f}% LEL.",
        })

    if permit.get("type", "").lower() in {"confined_space", "confined_space_entry"} and not permit.get("gas_test_valid", False):
        findings.append({"rule_id": "CONFINED-GAS-001", "severity": "hold", "reason": "A valid current gas-test record is required for this demo rule."})

    if permit.get("end"):
        end = datetime.fromisoformat(str(permit["end"]).replace("Z", "+00:00"))
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if now > end:
            findings.append({"rule_id": "PERMIT-EXPIRY-001", "severity": "suspend", "reason": "Permit validity window has expired."})

    decision = "suspend" if any(item["severity"] == "suspend" for item in findings) else "hold" if findings else "continue"
    return {
        "permit_id": permit.get("permit_id", permit.get("id")),
        "zone": permit.get("zone"),
        "type": permit.get("type"),
        "decision": decision,
        "rules": [item["rule_id"] for item in findings],
        "findings": findings,
    }
