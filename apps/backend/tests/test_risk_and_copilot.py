import unittest
import tempfile
from pathlib import Path

from app.services.dataset_service import get_incidents, get_permits, get_sensor_readings
from app.services.risk_model import compound_risk
from app.api.copilot import answer_question
from app.rag.retrieval.hybrid_retriever import retrieve
from app.rag.vectorstore.sqlite_store import SQLiteDocumentStore
from app.rag.ingest import ingest


class RiskAndDataTests(unittest.TestCase):
    def test_repository_datasets_are_loaded(self):
        self.assertEqual(get_sensor_readings()[-1]["value"], 6.2)
        self.assertEqual(get_permits()[0]["permit_id"], "PTW-4421")
        self.assertTrue(get_incidents())

    def test_compound_interaction_exceeds_individual_additive_score(self):
        base = {"methane_percent_lel": 6.2, "active_hot_work": True}
        combined = {**base, "maintenance_active": True, "shift_handover": True}
        baseline_score = compound_risk(base)["score"]
        combined_model = compound_risk(combined)
        self.assertGreater(combined_model["score"], baseline_score)
        self.assertTrue(any("Three-way" in item["label"] for item in combined_model["interactions"]))
        self.assertLessEqual(combined_model["score"], 99)

    def test_copilot_varies_by_intent_and_cites_dataset(self):
        permit_answer = answer_question("Can I start welding?")
        history_answer = answer_question("What was the previous near miss lesson?")
        self.assertIn("Suspend PTW-4421", permit_answer["answer"])
        self.assertIn("INC-2019-041", history_answer["answer"])
        self.assertNotEqual(permit_answer["answer"], history_answer["answer"])

    def test_regulation_retrieval_cites_current_code_and_oisd_abstains(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            store = SQLiteDocumentStore(Path(directory) / "regulations.sqlite3")
            current = retrieve("What must employers do about workplace hazards?", store=store)
            self.assertEqual(current[0]["id"], "OSHWC-2020-s6")
            oisd = retrieve("What clause does OISD STD 105 require for hot work?", store=store)
            self.assertEqual(oisd[0]["id"], "OISD-STD-105-index")
            self.assertIn("does not reproduce", oisd[0]["text"])

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
