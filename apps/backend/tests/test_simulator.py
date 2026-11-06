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
from evaluate_risk import evaluate_compound_risk, score_compound_risk  # noqa: E402
from agents.graph import run_agent_graph  # noqa: E402
from compound_risk import compound_risk  # noqa: E402


class SimulatorTests(unittest.TestCase):
    def test_multizone_stream_is_reproducible_and_labeled(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            manifest = generate(days=5, seed=7, output=first)
            generate(days=5, seed=7, output=second)
            self.assertEqual(manifest["zones"], ["Zone A", "Zone B", "Zone C"])
            self.assertEqual(manifest["sensor_rows"], 5 * 24 * 6 * 3)
            self.assertEqual(sum(manifest["incident_mechanisms"].values()), manifest["incident_count"])
            self.assertTrue({"combustible_gas_ramp", "work_control_conflict", "unobserved_precursor"}.issuperset(manifest["incident_mechanisms"]))
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
        self.assertNotIn("forecast", state)
        self.assertFalse(state["emergency_recommendation"]["external_actions_executed"])

    def test_compound_risk_is_scored_against_separate_incident_labels(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            data_dir = Path(directory) / "dataset"
            manifest = generate(days=5, seed=7, output=data_dir)
            report = evaluate_compound_risk(data_dir)
        self.assertEqual(report["labeled_windows"], manifest["sensor_rows"])
        self.assertEqual(report["positive_windows"], manifest["positive_windows"])
        self.assertEqual(len(report["compound_risk"]["metrics"]["incident_lead_times"]), manifest["incident_count"])
        self.assertEqual(len(report["methane_only_baseline"]["metrics"]["incident_lead_times"]), manifest["incident_count"])
        self.assertIn("false_alarm_rate", report["compound_risk"]["metrics"])
        self.assertIn("lead_minutes", report["compound_risk"]["metrics"]["incident_lead_times"][0])
        self.assertGreaterEqual(report["compound_risk"]["metrics"]["alert_episodes"], report["compound_risk"]["metrics"]["false_alarm_episodes"])

    def test_evaluator_uses_shared_compound_risk_implementation(self):
        row = {"methane_percent_lel": "2.4", "hot_work": "1", "maintenance": "0", "shift_handover": "1"}
        state = {"methane_percent_lel": 2.4, "active_hot_work": True, "maintenance_active": False, "shift_handover": True}
        self.assertEqual(score_compound_risk(row), compound_risk(state)["score"])


if __name__ == "__main__":
    unittest.main()
