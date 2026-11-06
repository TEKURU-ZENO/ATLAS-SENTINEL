import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DEFAULT_DB = Path(os.getenv("ATLAS_RAG_DB", Path(__file__).resolve().parents[5] / "datasets" / "regulations" / "rag.sqlite3"))


class SQLiteDocumentStore:
    """Persistent document text and citation metadata for local retrieval."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DEFAULT_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, body TEXT NOT NULL, metadata TEXT NOT NULL)")

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path)
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def upsert(self, document_id: str, text: str, metadata: dict | None = None) -> dict:
        with self._connect() as db:
            db.execute(
                "INSERT INTO documents(id, body, metadata) VALUES(?, ?, ?) ON CONFLICT(id) DO UPDATE SET body=excluded.body, metadata=excluded.metadata",
                (document_id, text, json.dumps(metadata or {}, ensure_ascii=True)),
            )
        return {"id": document_id, "status": "indexed", "characters": len(text)}

    def all(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id, body, metadata FROM documents ORDER BY id").fetchall()
        return [{"id": key, "text": body, **json.loads(metadata)} for key, body, metadata in rows]

    def count(self) -> int:
        with self._connect() as db:
            return db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
