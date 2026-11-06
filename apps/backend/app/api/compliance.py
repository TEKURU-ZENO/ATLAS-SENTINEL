from fastapi import APIRouter

from app.services.compliance_service import get_compliance_findings
from app.rag.retrieval.hybrid_retriever import retrieve

router = APIRouter()


@router.get("/findings")
def findings() -> dict:
    return get_compliance_findings()


@router.get("/search")
def search_regulations(q: str, limit: int = 5) -> dict:
    matches = retrieve(q, limit=max(1, min(limit, 10)))
    return {
        "query": q,
        "results": matches,
        "notice": "Retrieved text is source material, not legal advice. Check the current instrument and applicable state rules.",
    }
