from events.gas_leak import gas_leak_events
from events.maintenance_event import maintenance_event
from generators.permit_generator import generate_permit_stream
from generators.worker_generator import generate_worker_stream


def run_demo_scenario() -> list[dict]:
    events = []
    events.extend(gas_leak_events())
    events.append(maintenance_event())
    events.extend(generate_permit_stream())
    events.extend(generate_worker_stream())
    return sorted(events, key=lambda event: event["minute"])


if __name__ == "__main__":
    for event in run_demo_scenario():
        print(event)
