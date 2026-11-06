"""Chronological holdout comparison of rule and learned 30-60m warnings."""

import argparse
import csv
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "simulated"
FEATURES = ["methane_percent_lel", "gas_delta", "hot_work", "maintenance", "shift_handover", "occupancy"]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    by_zone = {}
    for row in rows:
        zone_rows = by_zone.setdefault(row["zone"], [])
        gas = float(row["methane_percent_lel"])
        previous = float(zone_rows[-1]["methane_percent_lel"]) if zone_rows else gas
        row["gas_delta"] = gas - previous
        zone_rows.append(row)
    return rows


def build_features(rows: list[dict]) -> list[list[float]]:
    return [[float(row[name]) for name in FEATURES] for row in rows]


def rule_score(row: dict) -> int:
    score = 8
    gas = float(row["methane_percent_lel"])
    if gas >= 1:
        score += min(30, round(gas * 4))
    active = set()
    if int(row["hot_work"]):
        score += 15
        active.add("hot_work")
    if int(row["maintenance"]):
        score += 10
        active.add("maintenance")
    if int(row["shift_handover"]):
        score += 8
        active.add("handover")
    if gas >= 1:
        active.add("methane")
    if {"methane", "hot_work"}.issubset(active):
        score += 18
    if {"methane", "maintenance"}.issubset(active):
        score += 8
    if {"hot_work", "handover"}.issubset(active):
        score += 7
    if {"maintenance", "handover"}.issubset(active):
        score += 5
    if {"methane", "hot_work", "handover"}.issubset(active):
        score += 8
    return min(99, score)


def metrics(y_true: list[int], predictions: list[int], rows: list[dict], incidents: list[dict]) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    false_alarm_rate = fp / (fp + tn) if fp + tn else 0.0
    zone_days = len(rows) / (24 * 60 / 10) if rows else 0
    prediction_keys = {(row["zone"], row["timestamp"]) for row, pred in zip(rows, predictions) if pred}
    leads = []
    detected = 0
    for incident in incidents:
        event_at = datetime.fromisoformat(incident["timestamp"])
        possible = []
        for zone, stamp in prediction_keys:
            if zone != incident["zone"]:
                continue
            lead = (event_at - datetime.fromisoformat(stamp)).total_seconds() / 60
            if 30 <= lead <= 60:
                possible.append(lead)
        if possible:
            detected += 1
            leads.append(max(possible))
    return {
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "false_alarm_rate_per_negative_window": round(false_alarm_rate, 4),
        "false_alarms_per_1000_windows": round(fp / max(len(rows), 1) * 1000, 2),
        "false_alarms_per_zone_day": round(fp / max(zone_days, 1), 2),
        "incident_lead_coverage": f"{detected}/{len(incidents)}",
        "median_lead_minutes": round(sorted(leads)[len(leads) // 2], 1) if leads else None,
        "confusion": {"true_positive": int(tp), "false_positive": int(fp), "false_negative": int(fn), "true_negative": int(tn)},
    }


def evaluate(data_dir: Path = DATA, threshold: float = 0.65) -> dict:
    rows = load_rows(data_dir / "sensor_stream.csv")
    split = int(len(rows) * 0.75)
    purge_rows = 6 * len({row["zone"] for row in rows})
    # Rows are interleaved across zones, so six ten-minute steps span 18 rows.
    train, test = rows[: split - purge_rows], rows[split + purge_rows :]
    x_train, y_train = build_features(train), [int(row["incident_30_60m"]) for row in train]
    x_test, y_test = build_features(test), [int(row["incident_30_60m"]) for row in test]
    model = HistGradientBoostingClassifier(max_iter=120, max_leaf_nodes=15, l2_regularization=2.0, random_state=42)
    model.fit(x_train, y_train)
    learned = [int(probability >= threshold) for probability in model.predict_proba(x_test)[:, 1]]
    rule_scores = [rule_score(row) for row in test]
    with (data_dir / "incidents.json").open(encoding="utf-8") as source:
        all_incidents = json.load(source)
    first_test_time = datetime.fromisoformat(test[0]["timestamp"]) + timedelta(minutes=60)
    test_incidents = [event for event in all_incidents if datetime.fromisoformat(event["timestamp"]) >= first_test_time]
    report = {
        "target": "incident precursor 30-60 minutes ahead",
        "split": {"strategy": "chronological 75/25 with 60-minute purge on both sides", "train_windows": len(train), "test_windows": len(test), "model_threshold": threshold},
        "model": {"name": "HistGradientBoostingClassifier", "features": FEATURES, "metrics": metrics(y_test, learned, test, test_incidents)},
        "rules_baseline": {
            "name": "ATLAS compound rule v1",
            "threshold_sweep": {
                str(cutoff): metrics(y_test, [int(score >= cutoff) for score in rule_scores], test, test_incidents)
                for cutoff in (35, 45, 60)
            },
        },
        "caveat": "Synthetic-data benchmark only. Event injection patterns and labels are simulator assumptions; no operational validity is implied.",
    }
    (data_dir / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--threshold", type=float, default=0.65)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.data, args.threshold), indent=2))
