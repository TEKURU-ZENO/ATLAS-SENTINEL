from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "ATLAS Sentinel"
    critical_risk_threshold: int = 80
    frontend_origins: list[str] = ["http://localhost:3000"]


settings = Settings(
    frontend_origins=[
        origin.strip()
        for origin in os.getenv("ATLAS_FRONTEND_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
)
