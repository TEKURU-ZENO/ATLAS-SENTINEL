from app.services.permit_service import validate_permits


def get_compliance_findings() -> dict:
    permit = validate_permits()
    findings = []
    if not permit["valid"]:
        findings.append(
            {
                "rule_family": "OISD",
                "violation": "Hot work active under elevated combustible gas conditions.",
                "action": "Suspend hot work and evacuate Zone C.",
            }
        )
    return {"findings": findings}
