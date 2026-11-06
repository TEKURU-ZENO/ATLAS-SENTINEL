import csv
from pathlib import Path


def load_csv(path: str) -> list[dict[str, str]]:
    source = Path(path)
    with source.open(newline="", encoding="utf-8-sig") as stream:
        return [
            {"source": source.name, "row": row_number, "text": " | ".join(f"{key}: {value}" for key, value in row.items())}
            for row_number, row in enumerate(csv.DictReader(stream), start=2)
        ]
