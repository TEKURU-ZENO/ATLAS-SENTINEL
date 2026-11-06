import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.vectorstore.sqlite_store import SQLiteDocumentStore


ROOT = Path(__file__).resolve().parents[5]
SEED_PATH = ROOT / "datasets" / "regulations" / "seed_chunks.json"
SYNONYMS = {
    "clean air": "ventilation free from dust noxious gas fumes",
    "air quality": "ventilation free from dust noxious gas fumes",
    "health hazards": "health hazard danger exposure",
    "come into force": "commencement effective date 21 november 2025 repeal",
    "effective date": "commencement 21 november 2025",
}


def normalize(text: str) -> str:
    text = text.lower().replace("-", " ")
    for phrase, expansion in SYNONYMS.items():
        if phrase in text:
            text += " " + expansion
    return text


def load_corpus(store: SQLiteDocumentStore | None = None) -> list[dict]:
    store = store or SQLiteDocumentStore()
    documents = store.all()
    present = {item["id"] for item in documents}
    seed_chunks = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    for chunk in seed_chunks:
        if chunk["id"] not in present:
            metadata = {key: value for key, value in chunk.items() if key != "text"}
            store.upsert(chunk["id"], chunk["text"], metadata)
    documents = store.all()
    return documents


def retrieve(query: str, limit: int = 5, store: SQLiteDocumentStore | None = None) -> list[dict]:
    query = query.strip()
    if not query:
        return []
    documents = load_corpus(store)
    if not documents:
        return []
    bodies = [normalize(" ".join(str(item.get(key, "")) for key in ("document", "section", "authority", "text"))) for item in documents]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
    matrix = vectorizer.fit_transform(bodies)
    query_vector = vectorizer.transform([normalize(query)])
    semantic_scores = cosine_similarity(query_vector, matrix).ravel()
    terms = {term.lower().rstrip("s") for term in re.findall(r"[\w-]+", normalize(query)) if len(term) > 2}
    ranked = []
    for index, document in enumerate(documents):
        content_terms = {term.rstrip("s") for term in re.findall(r"[\w-]+", bodies[index])}
        overlap = len(terms & content_terms) / max(1, len(terms))
        score = 0.82 * float(semantic_scores[index]) + 0.18 * overlap
        ranked.append({**document, "score": round(score, 4)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
