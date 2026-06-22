def evaluate_compliance(state: dict) -> dict:
    violations = []
    if state.get("permit_decision") == "suspend":
        violations.append("OISD hot work control violation")
    if state.get("workers", 0) > 0 and state.get("risk_score", 0) >= 80:
        violations.append("Factory Act preventive exposure control required")
    state["violations"] = violations
    return state
