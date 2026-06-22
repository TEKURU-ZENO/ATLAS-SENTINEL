from fastapi import FastAPI

from app.api import compliance, copilot, health, incidents, permits, risks, twin

app = FastAPI(title="ATLAS Sentinel API", version="0.1.0")

app.include_router(health.router)
app.include_router(risks.router, prefix="/risks", tags=["risks"])
app.include_router(twin.router, prefix="/twin", tags=["twin"])
app.include_router(permits.router, prefix="/permits", tags=["permits"])
app.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
