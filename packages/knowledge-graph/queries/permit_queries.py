def permit_overlap_query(permit_id: str) -> str:
    return f"MATCH (p:Permit {{id: '{permit_id}'}})-[:OVERLAPS]->(h:Hazard) RETURN p, h"
