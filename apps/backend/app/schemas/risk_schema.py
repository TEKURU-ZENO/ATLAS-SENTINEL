from pydantic import BaseModel


class RiskResponse(BaseModel):
    current: int
    forecast30: int
    forecast60: int
    reason: str
