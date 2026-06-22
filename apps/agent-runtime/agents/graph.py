from agents.compliance.compliance_agent import evaluate_compliance
from agents.emergency.emergency_response_agent import recommend_emergency_action
from agents.permits.permit_intelligence_agent import evaluate_permit
from agents.prediction.incident_forecasting_agent import forecast_incident
from agents.risk.hazard_correlation_agent import correlate_hazards


def run_agent_graph(state: dict) -> dict:
    state = correlate_hazards(state)
    state = evaluate_permit(state)
    state = evaluate_compliance(state)
    state = forecast_incident(state)
    if state["risk_score"] >= 80:
        state = recommend_emergency_action(state)
    return state
