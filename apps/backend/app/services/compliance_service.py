from app.services.permit_service import validate_permits
from app.services.risk_service import get_current_risk


def get_compliance_findings() -> dict:
    permit = validate_permits()
    risk = get_current_risk()
    findings = []
    for evaluation in permit["evaluations"]:
        if evaluation["decision"] in {"hold", "suspend"}:
            findings.extend({
                "rule_family": "configured_permit_interlock",
                "permit_id": evaluation["permit_id"],
                "rule_id": item["rule_id"],
                "finding": item["reason"],
                "action": "Review the permit and follow the approved site procedure.",
                "legal_conclusion": False,
            } for item in evaluation["findings"])
    return {
        "findings": findings,
        "risk_review": {
            "required": risk["current"] is not None and risk["current"] >= 60,
            "score": risk["current"],
            "status": risk["status"],
            "drivers": risk["drivers"],
            "interactions": risk["interactions"],
            "legal_references": ["OSHWC Code 2020, sections 6 and 23"] if risk["current"] is not None and risk["current"] >= 60 else [],
        },
        "notice": "These are configured operational checks, not a legal compliance determination.",
    }
