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
    sensor_citation = (
        {"source": f"Methane Sensor {twin['sensor_id']}", "detail": f"{twin['methane_percent_lel']:.1f}% LEL at {twin['sensor_timestamp']}"}
        if twin["methane_percent_lel"] is not None
        else {"source": "Sensor feed", "detail": "No sensor readings are available."}
    )
    citations = [sensor_citation]
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
        if twin["sensor_stale"] or not twin["sensor_verified"]:
            quality = "stale" if twin["sensor_stale"] else "unverified"
            answer = f"I cannot validate work authorization in {twin['zone']}: the sensor sample is {quality}. Treat the gas condition as unknown and obtain a fresh, verified reading through the approved site process before work proceeds."
            recommendation = "Hold the sensor-dependent permit check until fresh instrument data and authorization are verified."
        elif twin["active_hot_work"] and twin["methane_percent_lel"] >= 2.5:
            answer = f"Do not start or continue hot work in {twin['zone']}. Suspend {twin['permit_id']}, stop ignition sources, and have site safety verify gas readings and re-authorize the permit before work resumes."
            recommendation = "Suspend hot work; verify atmosphere; revalidate permit."
        else:
            answer = f"The dataset snapshot shows no active hot-work conflict in {twin['zone']}. Confirm a current gas test and permit authorization at the worksite before starting."
            recommendation = "Verify live gas test and permit at point of work."
    elif any(word in query for word in ("risk", "score", "why", "factors", "compound")):
        drivers = ", ".join(item["label"].lower() for item in risk["drivers"])
        overlaps = ", ".join(item["label"].lower() for item in risk["interactions"])
        if risk["current"] is None:
            if risk["status"] == "unavailable":
                answer = "A current compound-risk score is unavailable because no sensor sample is available."
            elif risk["status"] == "stale":
                answer = f"A current compound-risk score is unavailable because the latest sensor sample is stale. The last recorded sample scored {risk['snapshot_score']}/99, but that is not a current condition."
            else:
                answer = "A current compound-risk score is unavailable because this sensor source has not been verified."
            recommendation = "Obtain fresh verified sensor data before making a current-risk decision."
        else:
            answer = f"Compound risk is {risk['current']}/99 ({risk['level']}). Drivers: {drivers or 'none recorded'}. Interaction premiums: {overlaps or 'none'}. The score combines these signals rather than treating them independently."
            recommendation = f"Review the highest-scoring observed overlap: {risk['interactions'][0]['label'].lower()}." if risk["interactions"] else "Verify the recorded inputs and follow the site's approved risk-control procedure."
    elif any(word in query for word in ("incident", "history", "lesson", "previous", "near miss")):
        stop_words = {"what", "was", "the", "from", "about", "previous", "history", "incident", "incidents", "lesson", "lessons", "near", "miss", "case", "study", "public", "should", "we", "learn"}
        terms = {word.strip(".,?!") for word in query.split()} - stop_words
        cases = get_incidents()
        def case_text(item: dict) -> str:
            return " ".join(str(item.get(key, "")) for key in ("id", "title", "event_date", "location", "event_type", "signals", "outcome", "lesson", "source")).lower()

        ranked = sorted(
            cases,
            key=lambda item: sum(term in case_text(item) for term in terms),
            reverse=True,
        )
        best = ranked[0] if ranked else None
        has_match = bool(best and any(term in case_text(best) for term in terms))
        if has_match:
            answer = f"Public CSB case study, not a record from this plant: {best['title']} ({best['event_date']}) involved {best['event_type'].lower()}. Outcome: {best['outcome']} Lesson: {best['lesson']}"
            citations.append({"source": best["source"], "detail": best["id"], "url": best["source_url"]})
        else:
            answer = "The available incident archive contains public CSB case studies, not incidents from this plant. Ask about pipe opening, hydrogen sulfide, chemical storage, water intrusion, or corrosion to retrieve a specific case."
            for case in cases:
                citations.append({"source": case["source"], "detail": case["id"], "url": case["source_url"]})
        recommendation = "Use these public findings as learning prompts only; confirm controls against the applicable site hazards and approved procedures."
    elif any(word in query for word in ("sensor", "gas", "methane", "reading")):
        values = " -> ".join(f"{item['value']:.1f}%" for item in twin["sensor_history"])
        if twin["methane_percent_lel"] is None:
            answer = f"No sensor reading is available for {twin['zone']}; current gas conditions are unknown."
        else:
            quality = "stale" if twin["sensor_stale"] else "unverified" if not twin["sensor_verified"] else "within the configured freshness window"
            answer = f"Sensor {twin['sensor_id']} in {twin['zone']} recorded {values} LEL across the available sample. Latest recorded reading is {twin['methane_percent_lel']:.1f}% LEL at {twin['sensor_timestamp']}; it is {quality}."
        recommendation = "Verify against a current calibrated detector and the site's approved procedure."
    else:
        if risk["current"] is None:
            answer = f"Current gas and risk conditions are unavailable for {twin['zone']} because sensor data is {risk['status']}."
            if twin["methane_percent_lel"] is not None:
                answer += f" The last recorded value was {twin['methane_percent_lel']:.1f}% LEL at {twin['sensor_timestamp']}."
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
