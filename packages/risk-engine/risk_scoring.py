from compound_risk import compound_risk_score


def score_zone(state: dict) -> dict:
    score = compound_risk_score(state)
    return {"score": score, "tone": "red" if score >= 80 else "orange" if score >= 60 else "green"}
