"""Evaluate learned and shared compound-risk warnings against incident labels."""

import argparse
import csv
import json
import sys
import os
from statistics import median
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "simulated"
sys.path.insert(0, str(ROOT / "packages" / "risk-engine"))
from compound_risk import compound_risk  # noqa: E402

FEATURES = ["methane_percent_lel", "gas_delta", "hot_work", "maintenance", "shift_handover", "occupancy"]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    rows.sort(key=lambda row: (row["timestamp"], row["zone"]))
    by_zone = {}
    for row in rows:
        zone_rows = by_zone.setdefault(row["zone"], [])
        gas = float(row["methane_percent_lel"])
        previous = float(zone_rows[-1]["methane_percent_lel"]) if zone_rows else gas
        row["gas_delta"] = gas - previous
        zone_rows.append(row)
    return rows


def load_labeled_rows(data_dir: Path) -> list[dict]:
    """Join sensor features to the independently written ground-truth file."""
    rows = load_rows(data_dir / "sensor_stream.csv")
    with (data_dir / "incident_windows.csv").open(newline="", encoding="utf-8") as source:
        labels = list(csv.DictReader(source))
    labels_by_key = {}
    for label in labels:
        key = (label["timestamp"], label["zone"])
        if key in labels_by_key:
            raise ValueError(f"Duplicate incident label for {key}")
        labels_by_key[key] = label
    row_keys = {(row["timestamp"], row["zone"]) for row in rows}
    if len(row_keys) != len(rows) or row_keys != set(labels_by_key):
        raise ValueError("Sensor stream and incident_windows.csv keys do not match exactly")
    for row in rows:
        label = int(labels_by_key[(row["timestamp"], row["zone"])]["incident_30_60m"])
        if label not in (0, 1):
            raise ValueError(f"Incident label must be binary for {(row['timestamp'], row['zone'])}")
        row["incident_30_60m"] = label
    return rows


def build_features(rows: list[dict]) -> list[list[float]]:
    return [[float(row[name]) for name in FEATURES] for row in rows]


def score_compound_risk(row: dict) -> int:
    return compound_risk({
        "methane_percent_lel": float(row["methane_percent_lel"]),
        "active_hot_work": bool(int(row["hot_work"])),
        "maintenance_active": bool(int(row["maintenance"])),
        "shift_handover": bool(int(row["shift_handover"])),
    })["score"]


def metrics(y_true: list[int], predictions: list[int], rows: list[dict], incidents: list[dict], interval_minutes: int = 10) -> dict:
    if len(y_true) != len(predictions) or len(rows) != len(predictions):
        raise ValueError("Labels, predictions, and rows must have identical lengths")
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    false_alarm_rate = fp / (fp + tn) if fp + tn else 0.0
    zone_windows = {}
    for row in rows:
        zone_windows[row["zone"]] = zone_windows.get(row["zone"], 0) + 1
    zone_days = sum(count * interval_minutes / 1440 for count in zone_windows.values())
    prediction_keys = {(row["zone"], row["timestamp"]) for row, pred in zip(rows, predictions) if pred}
    predictions_by_zone = {}
    for row, prediction in zip(rows, predictions):
        if prediction:
            predictions_by_zone.setdefault(row["zone"], []).append((datetime.fromisoformat(row["timestamp"]), int(row["incident_30_60m"])))
    episodes = []
    for zone, alarms in predictions_by_zone.items():
        current = []
        previous = None
        for timestamp, label in sorted(alarms):
            if previous is not None and (timestamp - previous).total_seconds() > interval_minutes * 60:
                episodes.append(current)
                current = []
            current.append(label)
            previous = timestamp
        if current:
            episodes.append(current)
    false_alarm_episodes = sum(not any(episode) for episode in episodes)
    true_alarm_episodes = sum(any(episode) for episode in episodes)
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
    per_incident = []
    for incident in incidents:
        event_at = datetime.fromisoformat(incident["timestamp"])
        possible = []
        for zone, stamp in prediction_keys:
            if zone != incident["zone"]:
                continue
            lead = (event_at - datetime.fromisoformat(stamp)).total_seconds() / 60
            if 30 <= lead <= 60:
                possible.append(lead)
        per_incident.append({
            "incident_id": incident.get("incident_id"),
            "mechanism": incident.get("mechanism"),
            "zone": incident["zone"],
            "timestamp": incident["timestamp"],
            "detected": bool(possible),
            "lead_minutes": max(possible) if possible else None,
        })
    return {
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "false_alarm_rate": round(false_alarm_rate, 4),
        "false_alarm_rate_definition": "false-positive labeled windows / all negative labeled windows",
        "false_alarm_rate_per_negative_window": round(false_alarm_rate, 4),
        "false_alarms_per_1000_windows": round(fp / max(len(rows), 1) * 1000, 2),
        "false_alarms_per_zone_day": round(false_alarm_episodes / max(zone_days, 1e-9), 2),
        "false_alarm_windows_per_zone_day": round(fp / max(zone_days, 1e-9), 2),
        "alert_episodes": len(episodes),
        "false_alarm_episodes": false_alarm_episodes,
        "episode_precision": round(true_alarm_episodes / len(episodes), 4) if episodes else 0.0,
        "episode_definition": f"Consecutive predicted windows in a zone are one alert episode; an episode is true when any window overlaps a labeled 30-60 minute precursor window (sample interval {interval_minutes} minutes).",
        "incident_lead_coverage": f"{detected}/{len(incidents)}",
        "median_lead_minutes": round(median(leads), 1) if leads else None,
        "incident_lead_times": per_incident,
        "confusion": {"true_positive": int(tp), "false_positive": int(fp), "false_negative": int(fn), "true_negative": int(tn)},
    }


def evaluate(data_dir: Path = DATA, threshold: float = 0.65) -> dict:
    rows = load_labeled_rows(data_dir)
    split = int(len(rows) * 0.75)
    purge_rows = 6 * len({row["zone"] for row in rows})
    # Rows are interleaved across zones, so six ten-minute steps span 18 rows.
    train, test = rows[: split - purge_rows], rows[split + purge_rows :]
    x_train, y_train = build_features(train), [int(row["incident_30_60m"]) for row in train]
    x_test, y_test = build_features(test), [int(row["incident_30_60m"]) for row in test]
    model = HistGradientBoostingClassifier(max_iter=120, max_leaf_nodes=15, l2_regularization=2.0, random_state=42)
    model.fit(x_train, y_train)
    learned = [int(probability >= threshold) for probability in model.predict_proba(x_test)[:, 1]]
    rule_scores = [score_compound_risk(row) for row in test]
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
        "ground_truth_compound_risk": evaluate_compound_risk(data_dir),
        "experiment_design": {
            "data_kind": "synthetic only",
            "label_source": "incident_windows.csv joined by timestamp and zone",
            "direct_rule_scope": "Full-stream descriptive scoring of a fixed, untrained rule; not an independent holdout.",
            "learned_model_scope": "Chronological holdout within one simulator configuration and seed; not external validation.",
            "public_case_data": "CSB public cases are used for learning context only and are not joined to sensor labels.",
        },
        "caveat": "Synthetic-data benchmark only. Event injection patterns and labels are simulator assumptions; no operational validity is implied.",
    }
    (data_dir / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def evaluate_compound_risk(data_dir: Path = DATA, compound_threshold: int = 45, methane_threshold: float = 1.0) -> dict:
    """Score the shared production rule and a methane-only alarm on every labeled window."""
    rows = load_labeled_rows(data_dir)
    with (data_dir / "incidents.json").open(encoding="utf-8") as source:
        incidents = json.load(source)
    labels = [int(row["incident_30_60m"]) for row in rows]
    compound_scores = [score_compound_risk(row) for row in rows]
    compound_predictions = [int(score >= compound_threshold) for score in compound_scores]
    methane_predictions = [int(float(row["methane_percent_lel"]) >= methane_threshold) for row in rows]
    compound_metrics = metrics(labels, compound_predictions, rows, incidents)
    methane_metrics = metrics(labels, methane_predictions, rows, incidents)
    by_mechanism = {}
    for mechanism in sorted({item.get("mechanism", "unspecified") for item in incidents}):
        relevant = [item for item in compound_metrics["incident_lead_times"] if item.get("mechanism", "unspecified") == mechanism]
        detected = sum(item["detected"] for item in relevant)
        by_mechanism[mechanism] = {"detected": detected, "total": len(relevant), "coverage": f"{detected}/{len(relevant)}"}
    return {
        "evaluation_scope": "all sensor rows joined to incident_windows.csv by timestamp and zone",
        "labeled_windows": len(rows),
        "positive_windows": sum(labels),
        "compound_risk": {
            "source": "packages/risk-engine/compound_risk.py",
            "alarm_threshold": compound_threshold,
            "metrics": compound_metrics,
        },
        "methane_only_baseline": {
            "alarm_rule": f"methane_percent_lel >= {methane_threshold}% LEL",
            "metrics": methane_metrics,
        },
        "compound_incident_coverage_by_mechanism": by_mechanism,
        "interpretation": "Window-level classification metrics; incident lead time is the earliest qualifying alert window 30-60 minutes before each injected event. Repeated adjacent alert windows count separately in precision and false-alarm rate.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--threshold", type=float, default=0.65)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.data, args.threshold), indent=2))
