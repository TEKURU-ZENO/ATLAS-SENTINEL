import sys
from pathlib import Path


RISK_PACKAGE = Path(__file__).resolve().parents[4] / "packages" / "risk-engine"
if str(RISK_PACKAGE) not in sys.path:
    sys.path.insert(0, str(RISK_PACKAGE))

from compound_risk import compound_risk  # noqa: E402
