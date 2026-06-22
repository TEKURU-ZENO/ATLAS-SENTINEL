def answer_question(question: str, state: dict) -> dict:
    unsafe = state.get("risk_score", 0) >= 80 or state.get("permit_decision") == "suspend"
    return {
        "question": question,
        "answer": "Unsafe. Suspend work in Zone C." if unsafe else "Safe to proceed under active controls.",
        "citations": ["Permit PTW-4421", "Methane Sensor C-04", "OISD hot work control"],
    }
