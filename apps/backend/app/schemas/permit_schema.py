from pydantic import BaseModel


class PermitDecision(BaseModel):
    permit: str
    valid: bool
    decision: str
    evidence: str
