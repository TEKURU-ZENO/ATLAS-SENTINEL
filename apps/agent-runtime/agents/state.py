from typing import TypedDict


class SafetyState(TypedDict):
    zone: str
    methane_percent_lel: float
    active_hot_work: bool
    maintenance_active: bool
    shift_handover: bool
    workers: int
    risk_score: int
    findings: list[str]
