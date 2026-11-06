import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

from app.services.dataset_service import get_permits as source_permits


DB_PATH = Path(os.getenv("ATLAS_OPERATIONS_DB", Path(__file__).resolve().parents[4] / "datasets" / "simulated" / "operations.sqlite3"))


@contextmanager
def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        db.execute("CREATE TABLE IF NOT EXISTS permits (permit_id TEXT PRIMARY KEY, source_json TEXT NOT NULL, status TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS permit_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, permit_id TEXT NOT NULL, at TEXT NOT NULL, old_status TEXT NOT NULL, new_status TEXT NOT NULL, rule_ids TEXT NOT NULL, evidence TEXT NOT NULL)")
        for record in source_permits():
            db.execute("INSERT OR IGNORE INTO permits(permit_id, source_json, status) VALUES(?, ?, ?)", (record["permit_id"], json.dumps(record), record["status"].lower()))
        db.commit()
        yield db
    finally:
        db.close()


def get_permits() -> list[dict]:
    with _connect() as db:
        records = db.execute("SELECT source_json, status FROM permits ORDER BY permit_id").fetchall()
    return [{**json.loads(row["source_json"]), "status": row["status"]} for row in records]


def suspend(evaluations: list[dict]) -> list[str]:
    changed = []
    with _connect() as db:
        for evaluation in evaluations:
            if evaluation["decision"] != "suspend":
                continue
            permit_id = evaluation["permit_id"]
            row = db.execute("SELECT status FROM permits WHERE permit_id=?", (permit_id,)).fetchone()
            if not row or row["status"] != "active":
                continue
            now = datetime.now(timezone.utc).isoformat()
            db.execute("UPDATE permits SET status='suspended' WHERE permit_id=?", (permit_id,))
            db.execute(
                "INSERT INTO permit_audit(permit_id, at, old_status, new_status, rule_ids, evidence) VALUES(?, ?, ?, ?, ?, ?)",
                (permit_id, now, row["status"], "suspended", json.dumps(evaluation["rules"]), json.dumps(evaluation["findings"])),
            )
            changed.append(permit_id)
        db.commit()
    return changed


def audit_log() -> list[dict]:
    with _connect() as db:
        rows = db.execute("SELECT * FROM permit_audit ORDER BY id DESC").fetchall()
    return [{**dict(row), "rule_ids": json.loads(row["rule_ids"]), "evidence": json.loads(row["evidence"])} for row in rows]
