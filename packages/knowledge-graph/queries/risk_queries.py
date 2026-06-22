def zone_risk_query(zone: str) -> str:
    return f"MATCH (z:Zone {{name: '{zone}'}})-[*1..3]-(e) RETURN z, e"
