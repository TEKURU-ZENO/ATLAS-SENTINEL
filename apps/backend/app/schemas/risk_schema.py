from pydantic import BaseModel


class RiskResponse(BaseModel):
    current: int | None
    snapshot_score: int | None = None
    status: str
    sensor_trend: str
    sensor_delta: float | None = None
    reason: str
