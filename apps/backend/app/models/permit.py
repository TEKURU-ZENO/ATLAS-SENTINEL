from pydantic import BaseModel


class Permit(BaseModel):
    id: str
    type: str
    zone: str
    status: str
