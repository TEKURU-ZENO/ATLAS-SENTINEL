from fastapi import APIRouter
from app.services.dataset_service import get_incidents
from app.services.permit_service import evaluate_all_permits
from app.services.risk_service import get_current_risk
from app.services.twin_service import get_twin_state

router = APIRouter()


@router.get("")
def list_incidents() -> dict:
    items = get_incidents()
    return {"items": items, "count": len(items), "data_source": "repository_dataset_snapshot"}


@router.post("/emergency-workflow")
def trigger_emergency_workflow() -> dict:
    twin = get_twin_state()
    risk = get_current_risk()
    permit_result = evaluate_all_permits()
    actions = []
    if risk["current"] >= 60:
        actions.append(f"escalate {twin['zone']} compound risk to the site control room")
    for evaluation in permit_result["evaluations"]:
        if evaluation["decision"] == "suspend":
            actions.append(f"request authorized suspension of {evaluation['permit_id']}")
    actions.append("verify sensor state and follow the approved site emergency plan")
    return {
        "workflow": "recommendation",
        "executed": False,
        "actions": actions,
        "risk": risk,
        "permits": permit_result["evaluations"],
        "data_notice": twin["data_notice"],
    }
