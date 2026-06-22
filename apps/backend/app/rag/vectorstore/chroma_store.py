class ChromaStore:
    def upsert(self, document_id: str, text: str) -> dict[str, str]:
        return {"id": document_id, "status": "indexed", "preview": text[:80]}
