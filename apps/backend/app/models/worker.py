from pydantic import BaseModel


class Worker(BaseModel):
    id: str
    zone: str
    ppe_compliant: bool = True
