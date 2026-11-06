import json
from pathlib import Path

from app.rag.retrieval.hybrid_retriever import retrieve
from app.rag.vectorstore.sqlite_store import SQLiteDocumentStore


ROOT = Path(__file__).resolve().parents[4]
QUESTIONS = ROOT / "datasets" / "regulations" / "evaluation_questions.json"


def evaluate() -> dict:
    cases = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    store = SQLiteDocumentStore()
    results = []
    for case in cases:
        found = retrieve(case["question"], limit=3, store=store)
        context = " ".join(" ".join(str(item.get(key, "")) for key in ("document", "section", "authority", "text")).lower() for item in found)
        relevant = any(item["id"] == case["expected_source"] for item in found)
        citation_correct = bool(found and found[0]["id"] == case["expected_source"])
        facts_covered = all(term.lower() in context for term in case["expected_terms"])
        results.append({"id": case["id"], "retrieval_hit_at_3": relevant, "top1_citation_correct": citation_correct, "expected_facts_covered_in_context": facts_covered})
    count = len(results)
    report = {
        "question_count": count,
        "retrieval_recall_at_3": round(sum(row["retrieval_hit_at_3"] for row in results) / count, 4),
        "top1_citation_accuracy": round(sum(row["top1_citation_correct"] for row in results) / count, 4),
        "context_fact_coverage": round(sum(row["expected_facts_covered_in_context"] for row in results) / count, 4),
        "interpretation": "Context fact coverage is a retrieval proxy, not an LLM answer-correctness score. OISD-STD-105 clause-level cases intentionally test abstention until the authorized PDF is ingested.",
        "cases": results,
    }
    output = ROOT / "datasets" / "regulations" / "evaluation_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
