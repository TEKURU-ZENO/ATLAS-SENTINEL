def confidence(evidence_count: int) -> float:
    return min(0.55 + evidence_count * 0.1, 0.95)
