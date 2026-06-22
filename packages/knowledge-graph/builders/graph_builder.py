def build_demo_graph() -> list[tuple[str, str, str]]:
    return [
        ("Worker A", "WORKS_ON", "Boiler 7"),
        ("Boiler 7", "LOCATED_IN", "Zone C"),
        ("Zone C", "CONNECTED_TO", "Methane Sensor C-04"),
        ("PTW-4421", "OVERLAPS", "Methane Hazard"),
    ]
