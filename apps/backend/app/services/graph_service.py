def zone_c_relationships() -> list[tuple[str, str, str]]:
    return [
        ("Worker A", "WORKS_ON", "Boiler 7"),
        ("Boiler 7", "LOCATED_IN", "Zone C"),
        ("Zone C", "HAS_GAS_SENSOR", "Methane Sensor C-04"),
        ("PTW-4421", "AUTHORIZES", "Hot Work"),
    ]
