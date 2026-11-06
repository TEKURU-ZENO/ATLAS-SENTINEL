def evaluate_compliance(state: dict) -> dict:
    findings = []
    permit = state.get("permit_evaluation", {})
    if permit.get("decision") in {"hold", "suspend"}:
        findings.extend(permit.get("findings", []))
    if state.get("risk_score", 0) >= 60:
        findings.append({
            "rule_family": "operational_review",
            "finding": "Compound-risk review threshold reached.",
            "evidence": state.get("risk_interactions", []),
            "legal_reference": "OSHWC Code 2020, sections 6 and 23 are indexed as general employer safety duties; site-specific applicability needs competent review.",
        })
    state["compliance_findings"] = findings
    state["violations"] = findings
    return state
