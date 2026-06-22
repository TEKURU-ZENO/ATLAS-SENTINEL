def forecast(score: int) -> dict:
    return {"current": score, "in_30_min": min(score + 8, 99), "in_60_min": min(score + 11, 99)}
