from events.gas_leak import gas_leak_events


def generate_sensor_stream() -> list[dict]:
    return gas_leak_events()
