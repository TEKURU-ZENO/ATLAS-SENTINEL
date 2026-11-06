import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RULES_DIR = ROOT / "packages" / "safety-rules"
if str(RULES_DIR) not in sys.path:
    sys.path.insert(0, str(RULES_DIR))

from permit_rules import evaluate_permit as evaluate_permit_rules  # noqa: E402


def evaluate_permit(state: dict) -> dict:
    permit = state.get("permit") or {
        "permit_id": state.get("permit_id", "unknown"),
        "zone": state.get("zone"),
        "type": "hot_work" if state.get("active_hot_work") else "other",
        "status": "active" if state.get("active_hot_work") else "closed",
        "gas_test_valid": state.get("gas_test_valid", False),
    }
    result = evaluate_permit_rules(permit, state)
    state["permit_evaluation"] = result
    state["permit_decision"] = result["decision"]
    state["permit_findings"] = result["findings"]
    return state
