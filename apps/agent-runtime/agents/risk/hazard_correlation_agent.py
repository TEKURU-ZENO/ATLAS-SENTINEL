import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RISK_ENGINE = ROOT / "packages" / "risk-engine"
if str(RISK_ENGINE) not in sys.path:
    sys.path.insert(0, str(RISK_ENGINE))

from compound_risk import compound_risk  # noqa: E402


def correlate_hazards(state: dict) -> dict:
    model = compound_risk(state)
    state["risk_score"] = model["score"]
    state["risk_level"] = model["level"]
    state["risk_drivers"] = model["drivers"]
    state["risk_interactions"] = model["interactions"]
    state["risk_method"] = model["method"]
    state["findings"] = [item["label"] for item in model["drivers"] + model["interactions"]]
    return state
