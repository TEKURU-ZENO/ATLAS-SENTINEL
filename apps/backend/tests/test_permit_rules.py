import tempfile
import unittest
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from unittest.mock import patch

from app.services import permit_store
from app.services.permit_service import evaluate_permit
from app.services.permit_service import evaluate_all_permits


ACTIVE = {"permit_id": "PTW-4421", "zone": "Zone C", "type": "hot_work", "status": "active"}


class PermitRuleTests(unittest.TestCase):
    def test_hot_work_gas_at_threshold_suspends(self):
        result = evaluate_permit(ACTIVE, {"methane_percent_lel": 2.5})
        self.assertEqual(result["decision"], "suspend")
        self.assertIn("HOTWORK-GAS-001", result["rules"])

    def test_hot_work_below_threshold_continues(self):
        self.assertEqual(evaluate_permit(ACTIVE, {"methane_percent_lel": 2.49})["decision"], "continue")

    def test_missing_sensor_holds(self):
        result = evaluate_permit(ACTIVE, {"methane_percent_lel": None})
        self.assertEqual(result["decision"], "hold")
        self.assertIn("SENSOR-001", result["rules"])

    def test_confined_space_without_gas_test_holds(self):
        permit = {**ACTIVE, "type": "confined_space", "gas_test_valid": False}
        result = evaluate_permit(permit, {"methane_percent_lel": 0.2})
        self.assertEqual(result["decision"], "hold")
        self.assertIn("CONFINED-GAS-001", result["rules"])

    def test_expired_permit_suspends(self):
        now = datetime.now(timezone.utc)
        permit = {**ACTIVE, "end": (now - timedelta(minutes=1)).isoformat()}
        self.assertIn("PERMIT-EXPIRY-001", evaluate_permit(permit, {"methane_percent_lel": 0}, now)["rules"])

    def test_closed_permit_is_not_changed(self):
        self.assertEqual(evaluate_permit({**ACTIVE, "status": "closed"}, {})["decision"], "no_change")

    def test_suspend_persists_status_and_audit(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            with patch.object(permit_store, "DB_PATH", Path(directory) / "operations.sqlite3"):
                evaluation = evaluate_permit(ACTIVE, {"methane_percent_lel": 6.2})
                self.assertEqual(permit_store.suspend([evaluation]), ["PTW-4421"])
                self.assertEqual(permit_store.suspend([evaluation]), [])
                self.assertEqual(permit_store.audit_log()[0]["new_status"], "suspended")

    def test_permit_agent_suspends_matching_active_permit_when_enabled(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            fresh_snapshot = {"zone": "Zone C", "methane_percent_lel": 6.2, "sensor_stale": False, "sensor_verified": True}
            with patch.object(permit_store, "DB_PATH", Path(directory) / "operations.sqlite3"), patch.dict(os.environ, {"ATLAS_ENABLE_PERMIT_ACTIONS": "true"}), patch("app.services.permit_service.get_twin_state", return_value=fresh_snapshot):
                result = evaluate_all_permits(execute_suspensions=True)
                self.assertEqual(result["suspended"], ["PTW-4421"])
                status_by_id = {item["permit_id"]: item["status"] for item in permit_store.get_permits()}
                self.assertEqual(status_by_id["PTW-4421"], "suspended")

    def test_stale_sensor_holds_sensor_dependent_permit_check(self):
        stale_snapshot = {"zone": "Zone C", "methane_percent_lel": 6.2, "sensor_stale": True}
        with patch("app.services.permit_service.get_twin_state", return_value=stale_snapshot), patch("app.services.permit_service.get_permits", return_value=[ACTIVE]), patch("app.services.permit_service.audit_log", return_value=[]):
            result = evaluate_all_permits()
        self.assertEqual(result["evaluations"][0]["decision"], "hold")

    def test_fresh_but_unverified_sensor_holds_sensor_dependent_permit_check(self):
        unverified_snapshot = {"zone": "Zone C", "methane_percent_lel": 6.2, "sensor_stale": False, "sensor_verified": False}
        with patch("app.services.permit_service.get_twin_state", return_value=unverified_snapshot), patch("app.services.permit_service.get_permits", return_value=[ACTIVE]), patch("app.services.permit_service.audit_log", return_value=[]):
            result = evaluate_all_permits()
        self.assertEqual(result["evaluations"][0]["decision"], "hold")


if __name__ == "__main__":
    unittest.main()
