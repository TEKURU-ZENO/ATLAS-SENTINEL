import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from pathlib import Path

from app.services.dataset_service import get_incidents, get_permits, get_sensor_readings
from app.services.risk_model import compound_risk
from app.services.risk_service import get_current_risk
from app.services.compliance_service import get_compliance_findings
from app.api.incidents import trigger_emergency_workflow
from app.api.copilot import answer_question
from app.rag.retrieval.hybrid_retriever import retrieve
from app.rag.vectorstore.sqlite_store import SQLiteDocumentStore
from app.rag.ingest import ingest


class RiskAndDataTests(unittest.TestCase):
    def test_repository_datasets_are_loaded(self):
        self.assertEqual(get_sensor_readings()[-1]["value"], 6.2)
        self.assertEqual(get_permits()[0]["permit_id"], "PTW-4421")
        self.assertEqual(get_incidents()[0]["source_type"], "official_investigation")
        self.assertTrue(get_incidents()[0]["source_url"].startswith("https://www.csb.gov/"))

    def test_repository_sensor_sample_is_marked_stale_and_unverified(self):
        risk = get_current_risk()
        self.assertEqual(risk["data_source"], "repository_demo_sample_unknown_provenance")
        self.assertTrue("unverified source" in risk["data_notice"])
        self.assertTrue(risk["sensor_stale"])

    def test_missing_sensor_feed_returns_unavailable_instead_of_crashing(self):
        with patch("app.services.twin_service.get_sensor_readings", return_value=[]), patch("app.services.twin_service.get_permits", return_value=[]):
            risk = get_current_risk()
        self.assertIsNone(risk["current"])
        self.assertEqual(risk["status"], "unavailable")
        self.assertIsNone(risk["snapshot_score"])

    def test_fresh_but_unverified_sensor_does_not_become_current_risk(self):
        now = datetime.now(timezone.utc)
        rows = [
            {"timestamp": (now - timedelta(minutes=2)).isoformat(), "zone": "Zone C", "sensor": "C-04", "type": "methane", "value": 1.0, "unit": "percent_lel"},
            {"timestamp": now.isoformat(), "zone": "Zone C", "sensor": "C-04", "type": "methane", "value": 1.2, "unit": "percent_lel"},
        ]
        with patch("app.services.twin_service.get_sensor_readings", return_value=rows), patch("app.services.twin_service.get_permits", return_value=[]):
            risk = get_current_risk()
        self.assertEqual(risk["status"], "unverified")
        self.assertIsNone(risk["current"])

    def test_current_risk_does_not_masquerade_as_a_forecast(self):
        with patch.dict("os.environ", {"ATLAS_SENSOR_MAX_AGE_MINUTES": "15"}):
            risk = get_current_risk()
        self.assertEqual(risk["sensor_trend"], "rising")
        self.assertEqual(risk["sensor_delta"], 1.6)
        self.assertIsNone(risk["current"])
        self.assertEqual(risk["status"], "stale")
        self.assertGreater(risk["snapshot_score"], 0)
        self.assertEqual(risk["drivers"], [])
        self.assertTrue(risk["snapshot_drivers"])
        self.assertNotIn("forecast30", risk)
        self.assertNotIn("forecast60", risk)

    def test_compound_interaction_exceeds_individual_additive_score(self):
        base = {"methane_percent_lel": 6.2, "active_hot_work": True}
        combined = {**base, "maintenance_active": True, "shift_handover": True}
        baseline_score = compound_risk(base)["score"]
        combined_model = compound_risk(combined)
        self.assertGreater(combined_model["score"], baseline_score)
        self.assertTrue(any("Three-way" in item["label"] for item in combined_model["interactions"]))
        self.assertLessEqual(combined_model["score"], 99)

    def test_copilot_varies_by_intent_and_cites_dataset(self):
        with patch.dict("os.environ", {"ATLAS_SENSOR_MAX_AGE_MINUTES": "15"}):
            permit_answer = answer_question("Can I start welding?")
            history_answer = answer_question("What lesson did CSB identify from a pipe opening incident?")
            risk_answer = answer_question("What is the current risk score?")
        self.assertIn("stale", permit_answer["answer"])
        self.assertNotIn("Suspend PTW-4421", permit_answer["answer"])
        self.assertIn("PEMEX Deer Park", history_answer["answer"])
        self.assertIn("csb.gov", history_answer["citations"][-1]["url"])
        self.assertIn("not a record from this plant", history_answer["answer"])
        self.assertIn("score is unavailable", risk_answer["answer"])
        self.assertNotEqual(permit_answer["answer"], history_answer["answer"])

    def test_stale_snapshot_propagates_to_compliance_and_emergency_workflow(self):
        with patch.dict("os.environ", {"ATLAS_SENSOR_MAX_AGE_MINUTES": "15"}):
            compliance = get_compliance_findings()
            workflow = trigger_emergency_workflow()
        self.assertEqual(compliance["risk_review"]["status"], "stale")
        self.assertFalse(compliance["risk_review"]["required"])
        self.assertTrue(any("Current compound risk is unavailable" in action for action in workflow["actions"]))
        self.assertFalse(workflow["executed"])

    def test_regulation_retrieval_cites_current_code_and_oisd_abstains(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            store = SQLiteDocumentStore(Path(directory) / "regulations.sqlite3")
            current = retrieve("What must employers do about workplace hazards?", store=store)
            self.assertEqual(current[0]["id"], "OSHWC-2020-s6")
            oisd = retrieve("What clause does OISD STD 105 require for hot work?", store=store)
            self.assertEqual(oisd[0]["id"], "OISD-STD-105-index")
            self.assertIn("does not reproduce", oisd[0]["text"])
            self.assertEqual(retrieve("Tell me a joke", store=store), [])

    def test_local_text_ingestion_retains_source_citation_metadata(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            source = Path(directory) / "permit-standard.txt"
            source.write_text("SECTION 6 - WORK PERMIT\nA permit shall identify the work area and hazard controls.", encoding="utf-8")
            store = SQLiteDocumentStore(Path(directory) / "documents.sqlite3")
            result = ingest(source, store)
            record = store.all()[0]
            self.assertEqual(result["indexed_chunks"], 1)
            self.assertEqual(record["document"], "permit-standard.txt")
            self.assertIsNone(record["page"])


if __name__ == "__main__":
    unittest.main()
