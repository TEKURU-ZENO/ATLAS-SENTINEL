from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.permit_service import evaluate_all_permits, validate_permits

router = APIRouter()


@router.get("/validate")
def validate() -> dict:
    return validate_permits()


class ActionRequest(BaseModel):
    execute_suspensions: bool = False


@router.post("/evaluate")
def evaluate(payload: ActionRequest) -> dict:
    try:
        return evaluate_all_permits(payload.execute_suspensions)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
