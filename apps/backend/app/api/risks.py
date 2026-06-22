from fastapi import APIRouter

from app.services.risk_service import get_current_risk

router = APIRouter()


@router.get("/current")
def current_risk() -> dict:
    return get_current_risk()
