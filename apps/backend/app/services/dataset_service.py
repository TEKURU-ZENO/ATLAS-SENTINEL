import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "datasets"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def get_sensor_readings() -> list[dict]:
    rows = read_csv(DATASET_ROOT / "sensors" / "sensor_history.csv")
    return [
        {**row, "value": float(row["value"])}
        for row in sorted(rows, key=lambda item: item["timestamp"])
    ]


def get_permits() -> list[dict]:
    return read_csv(DATASET_ROOT / "permits" / "permit_records.csv")


def get_incidents() -> list[dict]:
    path = DATASET_ROOT / "incidents" / "public_case_studies.json"
    return json.loads(path.read_text(encoding="utf-8"))
