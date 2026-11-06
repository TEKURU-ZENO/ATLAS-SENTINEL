from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dataset_service import get_incidents
from app.services.risk_service import get_current_risk
from app.services.twin_service import get_twin_state
from app.rag.retrieval.hybrid_retriever import retrieve

router = APIRouter()


class Question(BaseModel):
    question: str


def answer_question(question: str) -> dict:
    twin = get_twin_state()
    risk = get_current_risk()
    query = question.lower()
    citations = [
        {"source": f"Methane Sensor {twin['sensor_id']}", "detail": f"{twin['methane_percent_lel']:.1f}% LEL at {twin['sensor_timestamp']}"},
    ]
    if twin["permit_id"]:
        citations.append({"source": f"Permit {twin['permit_id']}", "detail": f"Active { 'hot-work' if twin['active_hot_work'] else 'work' } permit for {twin['equipment']} in {twin['zone']}"})

    if any(word in query for word in ("regulation", "statute", "law", "code", "oisd", "factory", "standard", "section")):
        matches = retrieve(question, limit=3)
        if matches and matches[0]["score"] >= 0.08:
            best = matches[0]
            citations = [
                {"source": f"{best.get('document', 'Source')} {best.get('section', '')}".strip(), "detail": best["text"], "url": best.get("source_url"), "page": best.get("page")}
            ]
            answer = best["text"]
            recommendation = "Confirm applicability and the current official text; this retrieval is not a legal determination."
        else:
            answer = "No matching regulatory passage is indexed. Add the authorized document to the regulation source folder and run the ingestion command before relying on a clause-level answer."
            recommendation = "Consult the current official instrument and site legal/compliance owner."
        return {"question": question, "answer": answer, "recommendation": recommendation, "citations": citations, "risk": risk, "data_source": twin["data_source"], "data_notice": twin["data_notice"]}

    if any(word in query for word in ("permit", "weld", "hot work", "start work", "start welding")):
        if twin["active_hot_work"] and twin["methane_percent_lel"] >= 2.5:
            answer = f"Do not start or continue hot work in {twin['zone']}. Suspend {twin['permit_id']}, stop ignition sources, and have site safety verify gas readings and re-authorize the permit before work resumes."
            recommendation = "Suspend hot work; verify atmosphere; revalidate permit."
        else:
            answer = f"The dataset snapshot shows no active hot-work conflict in {twin['zone']}. Confirm a current gas test and permit authorization at the worksite before starting."
            recommendation = "Verify live gas test and permit at point of work."
    elif any(word in query for word in ("risk", "score", "why", "factors", "compound")):
        drivers = ", ".join(item["label"].lower() for item in risk["drivers"])
        overlaps = ", ".join(item["label"].lower() for item in risk["interactions"])
        answer = f"Compound risk is {risk['current']}/99 ({risk['level']}). Drivers: {drivers or 'none recorded'}. Interaction premiums: {overlaps or 'none'}. The score combines these signals rather than treating them independently."
        recommendation = "Resolve the highest-risk overlap first: combustible gas with ignition work."
    elif any(word in query for word in ("incident", "history", "lesson", "previous", "near miss")):
        matches = [incident for incident in get_incidents() if incident["zone"].lower() == twin["zone"].lower()]
        if matches:
            incident = matches[0]
            answer = f"A recorded {incident['outcome'].replace('_', ' ')} ({incident['id']}) in {incident['zone']} involved {', '.join(incident['signals']).replace('_', ' ')}. Lesson: {incident['lesson']}"
            citations.append({"source": incident["id"], "detail": incident["lesson"]})
        else:
            answer = f"No matching historical incident is present for {twin['zone']} in the loaded incident dataset."
        recommendation = "Use the lesson as a control prompt; it is not a substitute for site procedure."
    elif any(word in query for word in ("sensor", "gas", "methane", "reading")):
        values = " -> ".join(f"{item['value']:.1f}%" for item in twin["sensor_history"])
        answer = f"Sensor {twin['sensor_id']} in {twin['zone']} recorded {values} LEL across the available sample. Latest reading is {twin['methane_percent_lel']:.1f}% LEL at {twin['sensor_timestamp']}."
        recommendation = "Treat this repository snapshot as historical; verify against the live calibrated detector."
    else:
        answer = f"Current snapshot: {twin['zone']} has {twin['methane_percent_lel']:.1f}% LEL, risk {risk['current']}/99 ({risk['level']}), and {'an active hot-work permit' if twin['active_hot_work'] else 'no active hot-work permit'}. Ask about risk drivers, gas readings, permits, or incident lessons for a focused assessment."
        recommendation = "Confirm critical conditions using live site instrumentation and procedures."

    return {
        "question": question,
        "answer": answer,
        "recommendation": recommendation,
        "citations": citations,
        "risk": risk,
        "data_source": twin["data_source"],
        "data_notice": twin["data_notice"],
    }


@router.post("/ask")
def ask(payload: Question) -> dict:
    return answer_question(payload.question)


@router.get("/ask")
def ask_compat(question: str = "What is the current risk?") -> dict:
    return answer_question(question)
