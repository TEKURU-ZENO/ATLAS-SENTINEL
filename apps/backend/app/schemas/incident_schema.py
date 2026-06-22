from pydantic import BaseModel


class EmergencyWorkflowResponse(BaseModel):
    workflow: str
    actions: list[str]
