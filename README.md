# ATLAS Sentinel (Under Revamp)

Industrial safety decision-support prototype.

ATLAS Sentinel is a research/demo prototype. The repository includes a reproducible synthetic plant dataset, an explainable compound-risk rules baseline, an experimental learned-model benchmark, data-backed API routes, permit rule evaluation, and local regulatory retrieval. It is not connected to live plant systems and is not validated for safety-critical decisions.

## What Is Built

- Next.js frontend and FastAPI endpoints for risk, twin, permits, incidents, compliance, and copilot.
- 21-day, three-zone simulator with deterministic sensor, permit, shift, maintenance, occupancy, and precursor streams.
- Compound-risk rules baseline with explicit drivers/interactions; gradient-boosting holdout evaluation and false-alarm/lead-time metrics.
- Permit decisions with rule identifiers, a SQLite audit-backed local mirror, and an explicit environment gate for demo suspensions.
- Local TF-IDF regulation retrieval with section/page citations, a 50-question retrieval/citation evaluation, and PDF ingestion tools.
- Current-law seed context for India's OSH Code. OISD-STD-105 is indexed only as a catalogue record until its authorized full text is provided.

## Data and Evaluation

```powershell
npm run sim:generate
npm run sim:evaluate
npm run test:backend
npm run rag:evaluate
```

The checked-in simulator output and evaluation are synthetic benchmarks, not observed incident data. To test local permit suspension, set `ATLAS_ENABLE_PERMIT_ACTIONS=true` and call `POST /permits/evaluate` with `{"execute_suspensions": true}`. This changes only the local audited demo mirror, never an external permit system.

Regulatory document ingestion and source limits are documented in `datasets/regulations/README.md`.

## Run the App

In one PowerShell terminal, install and run the API:

```powershell
pip install -r apps/backend/requirements.txt
$env:ATLAS_FRONTEND_ORIGINS = "http://localhost:3000"
python -m uvicorn app.main:app --app-dir apps/backend --reload
```

In a second terminal, run the frontend:

```powershell
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm run dev
```

Example environment files are in `apps/frontend/` and `apps/backend/`. For Vercel, set `NEXT_PUBLIC_API_URL` to the separately deployed API URL in the frontend project's environment settings. Without it, the interface reports the API unavailable rather than displaying invented live state.

## Monorepo Map

```text
apps/frontend       Next.js command center shell
apps/backend        FastAPI service boundary
apps/agent-runtime  Synchronous rules-based agent graph
apps/simulator      Digital twin event simulator
packages/*          Shared compound risk and permit rules plus UI/types
datasets            Historical snapshots, generated simulation, regulation sources
architecture        System diagrams and sequence flows
deployment          Deployment notes and local compose plan
```

## Not Connected Yet

- Live sensor/permit/CMMS sources, authentication, and a production-grade persistence service.
- Authorized full-text OISD-STD-105 and the current jurisdiction-specific implementing rules.
- An LLM answer-generation layer; copilot currently does intent routing and source-grounded deterministic responses.
- Field validation and independent safety-case approval of thresholds, model features, labels, and performance.

