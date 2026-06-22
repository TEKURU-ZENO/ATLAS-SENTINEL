from fastapi import APIRouter

from app.services.compliance_service import get_compliance_findings

router = APIRouter()


@router.get("/findings")
def findings() -> dict:
    return get_compliance_findings()
