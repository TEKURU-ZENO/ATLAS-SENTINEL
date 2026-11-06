import csv
import sys
import tempfile
import unittest
from pathlib import Path


SIMULATOR = Path(__file__).resolve().parents[2] / "simulator"
AGENT_RUNTIME = Path(__file__).resolve().parents[2] / "agent-runtime"
sys.path.insert(0, str(SIMULATOR))
sys.path.insert(0, str(AGENT_RUNTIME))
from generate_dataset import generate  # noqa: E402
from agents.graph import run_agent_graph  # noqa: E402


class SimulatorTests(unittest.TestCase):
    def test_multizone_stream_is_reproducible_and_labeled(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            manifest = generate(days=5, seed=7, output=first)
            generate(days=5, seed=7, output=second)
            self.assertEqual(manifest["zones"], ["Zone A", "Zone B", "Zone C"])
            self.assertEqual(manifest["sensor_rows"], 5 * 24 * 6 * 3)
            with (first / "sensor_stream.csv").open(encoding="utf-8", newline="") as a, (second / "sensor_stream.csv").open(encoding="utf-8", newline="") as b:
                self.assertEqual(list(csv.DictReader(a)), list(csv.DictReader(b)))
            with (first / "incident_windows.csv").open(encoding="utf-8", newline="") as source:
                rows = list(csv.DictReader(source))
            self.assertTrue(any(row["incident_30_60m"] == "1" for row in rows))
            self.assertTrue((first / "permits.csv").exists())
            self.assertTrue((first / "maintenance_windows.csv").exists())
            self.assertTrue((first / "shifts.csv").exists())

    def test_agent_graph_uses_shared_risk_and_permit_rules(self):
        state = run_agent_graph({
            "zone": "Zone C",
            "permit_id": "PTW-4421",
            "methane_percent_lel": 6.2,
            "active_hot_work": True,
            "maintenance_active": True,
            "shift_handover": True,
        })
        self.assertEqual(state["risk_score"], 99)
        self.assertEqual(state["permit_decision"], "suspend")
        self.assertFalse(state["emergency_recommendation"]["external_actions_executed"])


if __name__ == "__main__":
    unittest.main()
