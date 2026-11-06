from fastapi import APIRouter
from fastapi import HTTPException
import json
from pathlib import Path

from app.services.risk_service import get_current_risk

router = APIRouter()
EVALUATION_FILE = Path(__file__).resolve().parents[4] / "datasets" / "simulated" / "evaluation.json"


@router.get("/current")
def current_risk() -> dict:
    return get_current_risk()


@router.get("/evaluation")
def risk_evaluation() -> dict:
    if not EVALUATION_FILE.exists():
        raise HTTPException(status_code=404, detail="Run the simulator risk evaluation first.")
    return json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
