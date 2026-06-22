class Neo4jClient:
    def run(self, query: str) -> list[dict]:
        return [{"query": query, "status": "stub"}]
