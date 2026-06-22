from pydantic import BaseModel


class Incident(BaseModel):
    id: str
    zone: str
    severity: str
