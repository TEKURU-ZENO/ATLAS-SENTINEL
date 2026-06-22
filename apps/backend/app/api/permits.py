from fastapi import APIRouter

from app.services.permit_service import validate_permits

router = APIRouter()


@router.get("/validate")
def validate() -> dict:
    return validate_permits()
