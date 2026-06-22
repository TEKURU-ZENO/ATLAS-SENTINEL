def correlate_hazards(state: dict) -> dict:
    score = 18
    findings = []
    if state.get("methane_percent_lel", 0) >= 2.5:
        score += 25
        findings.append("Methane concentration is rising.")
    if state.get("active_hot_work"):
        score += 20
        findings.append("Hot work permit is active.")
    if state.get("maintenance_active"):
        score += 12
        findings.append("Maintenance is active on linked equipment.")
    if state.get("shift_handover"):
        score += 11
        findings.append("Shift handover is in progress.")
    state["risk_score"] = min(score, 99)
    state["findings"] = findings
    return state
