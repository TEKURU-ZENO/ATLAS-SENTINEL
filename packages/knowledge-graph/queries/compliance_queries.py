def violation_query(zone: str) -> str:
    return f"MATCH (z:Zone {{name: '{zone}'}})-[:VIOLATES]->(r:Regulation) RETURN z, r"
