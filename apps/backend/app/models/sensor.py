from pydantic import BaseModel


class Sensor(BaseModel):
    id: str
    zone: str
    type: str
    value: float
