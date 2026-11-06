"""Generate reproducible synthetic plant operations and incident labels."""

import argparse
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "datasets" / "simulated"
ZONES = {"Zone A": 0.15, "Zone B": 0.3, "Zone C": 0.45}
STEP_MINUTES = 10


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(days: int = 21, seed: int = 20261106, output: Path = OUT) -> dict:
    rng = random.Random(seed)
    start = datetime(2025, 1, 6, tzinfo=timezone.utc)
    steps = days * 24 * 60 // STEP_MINUTES
    incident_marks = []
    mechanisms = ("combustible_gas_ramp", "work_control_conflict", "unobserved_precursor")
    for zone in ZONES:
        for day in range(1, days, max(1, days // 6)):
            mechanism = rng.choices(mechanisms, weights=(0.45, 0.3, 0.25), k=1)[0]
            if mechanism == "work_control_conflict":
                event_time = start + timedelta(days=day, hours=rng.choice([8, 16]), minutes=40)
            else:
                hour = rng.randint(7, 20)
                minute = rng.choice([0, 10, 20, 30, 40, 50])
                event_time = start + timedelta(days=day, hours=hour, minutes=minute)
            incident_marks.append((zone, event_time, mechanism))

    nuisance_gas = {zone: [] for zone in ZONES}
    for zone in ZONES:
        for day in range(days):
            if rng.random() >= 0.4:
                continue
            timestamp = start + timedelta(days=day, hours=rng.randint(6, 21), minutes=rng.choice([0, 10, 20, 30, 40, 50]))
            if any(event_zone == zone and abs((event_time - timestamp).total_seconds()) <= 90 * 60 for event_zone, event_time, _ in incident_marks):
                continue
            nuisance_gas[zone].append((timestamp, rng.uniform(0.8, 1.2)))

    permits = []
    maintenance = []
    shifts = []
    for zone, event_time, mechanism in incident_marks:
        if mechanism == "work_control_conflict":
            permit_start = event_time - timedelta(hours=1)
            permit_end = event_time + timedelta(minutes=10)
            permits.append({"permit_id": f"SIM-PTW-{zone[-1]}-{event_time:%j%H%M}", "zone": zone, "type": "hot_work", "start": permit_start, "end": permit_end, "status": "scheduled"})
            maintenance.append({"work_order": f"SIM-WO-{zone[-1]}-{event_time:%j%H%M}", "zone": zone, "equipment": f"{zone[-1]}-PUMP-SIM", "start": permit_start, "end": permit_end})
    for zone in ZONES:
        for day in range(days):
            midnight = start + timedelta(days=day)
            for shift_start in (0, 8, 16):
                shifts.append({"zone": zone, "start": midnight + timedelta(hours=shift_start), "end": midnight + timedelta(hours=shift_start + 8), "crew": f"{zone[-1]}-{shift_start // 8 + 1}"})
            if rng.random() < 0.62:
                begin = midnight + timedelta(hours=rng.randint(6, 18), minutes=rng.choice([0, 30]))
                permits.append({"permit_id": f"PTW-{zone[-1]}-{day + 1:03d}", "zone": zone, "type": "hot_work", "start": begin, "end": begin + timedelta(hours=rng.randint(1, 4)), "status": "scheduled"})
            if rng.random() < 0.48:
                begin = midnight + timedelta(hours=rng.randint(0, 21), minutes=rng.choice([0, 30]))
                maintenance.append({"work_order": f"WO-{zone[-1]}-{day + 1:03d}", "zone": zone, "equipment": f"{zone[-1]}-PUMP-{day % 4 + 1}", "start": begin, "end": begin + timedelta(hours=rng.randint(1, 5))})

    sensor_rows, outcome_rows = [], []
    incidents = []
    for zone, event_time, mechanism in incident_marks:
        incidents.append({"incident_id": f"SIM-{len(incidents) + 1:04d}", "zone": zone, "timestamp": event_time.isoformat(), "outcome": "precursor_event", "mechanism": mechanism, "injected": True})

    for zone, baseline in ZONES.items():
        zone_events = [(at, mechanism) for event_zone, at, mechanism in incident_marks if event_zone == zone]
        for index in range(steps):
            timestamp = start + timedelta(minutes=index * STEP_MINUTES)
            active_event = next(((at, mechanism) for at, mechanism in zone_events if timedelta(minutes=-10) <= at - timestamp <= timedelta(minutes=70)), None)
            noise = rng.uniform(-0.08, 0.08)
            gas = max(0.02, baseline + noise + rng.uniform(0, 0.12))
            if active_event:
                event_time, mechanism = active_event
                minutes_to_event = (event_time - timestamp).total_seconds() / 60
                if mechanism == "combustible_gas_ramp" and 0 <= minutes_to_event <= 60:
                    gas += (60 - minutes_to_event) / 60 * rng.uniform(1.8, 3.4)
                elif mechanism == "combustible_gas_ramp" and -10 <= minutes_to_event < 0:
                    gas += rng.uniform(3.5, 6.0)
            nuisance = [value for nuisance_at, value in nuisance_gas[zone] if nuisance_at <= timestamp < nuisance_at + timedelta(minutes=20)]
            if nuisance:
                gas += max(nuisance)
            hot_work = any(p["zone"] == zone and p["start"] <= timestamp < p["end"] for p in permits)
            maint = any(m["zone"] == zone and m["start"] <= timestamp < m["end"] for m in maintenance)
            handover = timestamp.minute < 20 and timestamp.hour in (0, 8, 16)
            crew = next((s["crew"] for s in shifts if s["zone"] == zone and s["start"] <= timestamp < s["end"]), "unknown")
            occupancy = max(0, int(rng.gauss(5 if hot_work else 3, 2)))
            future_minutes = min(((at - timestamp).total_seconds() / 60 for at, _ in zone_events if at > timestamp), default=None)
            target = int(future_minutes is not None and 30 <= future_minutes <= 60)
            row = {
                "timestamp": timestamp.isoformat(), "zone": zone, "sensor_id": f"{zone[-1]}-GAS-01",
                "methane_percent_lel": round(gas, 3), "temperature_c": round(rng.gauss(31 if maint else 28, 2), 2),
                "hot_work": int(hot_work), "maintenance": int(maint), "shift_handover": int(handover),
                "occupancy": occupancy, "crew_id": crew, "incident_30_60m": target,
            }
            sensor_rows.append(row)
            outcome_rows.append({"timestamp": timestamp.isoformat(), "zone": zone, "incident_30_60m": target, "minutes_to_incident": round(future_minutes, 1) if future_minutes is not None else ""})

    sensor_rows.sort(key=lambda row: (row["timestamp"], row["zone"]))
    outcome_rows.sort(key=lambda row: (row["timestamp"], row["zone"]))
    serialized_permits = [{**p, "start": p["start"].isoformat(), "end": p["end"].isoformat()} for p in permits]
    serialized_maintenance = [{**m, "start": m["start"].isoformat(), "end": m["end"].isoformat()} for m in maintenance]
    serialized_shifts = [{**s, "start": s["start"].isoformat(), "end": s["end"].isoformat()} for s in shifts]
    write_csv(output / "sensor_stream.csv", sensor_rows)
    write_csv(output / "permits.csv", serialized_permits)
    write_csv(output / "maintenance_windows.csv", serialized_maintenance)
    write_csv(output / "shifts.csv", serialized_shifts)
    write_csv(output / "incident_windows.csv", outcome_rows)
    (output / "incidents.json").write_text(json.dumps(incidents, indent=2), encoding="utf-8")
    manifest = {
        "kind": "synthetic_simulation",
        "seed": seed,
        "days": days,
        "zones": list(ZONES),
        "sample_interval_minutes": STEP_MINUTES,
        "sensor_rows": len(sensor_rows),
        "incident_count": len(incidents),
        "incident_mechanisms": {mechanism: sum(item["mechanism"] == mechanism for item in incidents) for mechanism in mechanisms},
        "nuisance_gas_excursions": sum(len(items) for items in nuisance_gas.values()),
        "positive_windows": sum(row["incident_30_60m"] for row in sensor_rows),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limitations": "Synthetic process, schedules, and event injection; not field telemetry or a validated safety threshold model.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=20261106)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps(generate(args.days, args.seed, args.output), indent=2))
