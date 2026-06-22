from fastapi import APIRouter

from app.services.twin_service import get_twin_state

router = APIRouter()


@router.get("/state")
def twin_state() -> dict:
    return get_twin_state()
