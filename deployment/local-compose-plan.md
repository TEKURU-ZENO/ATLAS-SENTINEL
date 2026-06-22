# Local Deployment Plan

The MVP can run as three services:

- `frontend`: Next.js command center.
- `backend`: FastAPI API and websocket stream.
- `simulator`: Python process that emits plant events.

Future services:

- Postgres for incident and permit persistence.
- Neo4j for the industrial knowledge graph.
- Chroma for regulation retrieval.
