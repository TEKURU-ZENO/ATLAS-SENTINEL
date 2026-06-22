from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ATLAS Sentinel"
    critical_risk_threshold: int = 80


settings = Settings()
