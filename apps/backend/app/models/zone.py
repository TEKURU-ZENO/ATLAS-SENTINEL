from pydantic import BaseModel


class Zone(BaseModel):
    id: str
    risk_score: int
    worker_count: int
