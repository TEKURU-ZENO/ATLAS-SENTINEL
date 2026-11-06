# ATLAS Sentinel (Under Revamp)

Industrial safety decision-support prototype.

ATLAS Sentinel is a research/demo prototype. The repository includes a reproducible synthetic plant dataset, an explainable compound-risk rules baseline, an experimental learned-model benchmark, data-backed API routes, permit rule evaluation, and local regulatory retrieval. It is not connected to live plant systems and is not validated for safety-critical decisions.

## What Is Built

- Next.js frontend and FastAPI endpoints for risk, twin, permits, incidents, compliance, and copilot.
- 21-day, three-zone synthetic simulator with deterministic sensor, permit, shift, maintenance, occupancy, and injected precursor streams.
- Shared compound-risk rules evaluated against `incident_windows.csv` and a methane-only baseline, with window precision/false-alarm rate, alert-episode burden, and per-event lead times. A separate temporal ML experiment is explicitly synthetic-only.
- Curated, cited CSB public investigation case studies for lessons and source-grounded responses. These cases are not treated as plant incidents or model labels.
- Permit decisions with rule identifiers, a SQLite audit-backed local mirror, and an explicit environment gate for demo suspensions.
- Sensor freshness gating: old or unverified samples do not produce a current risk score, and sensor-dependent permit checks hold by default after 15 minutes.
- Local TF-IDF regulation retrieval with section/page citations, a 50-question retrieval/citation evaluation, and PDF ingestion tools.
- Current-law seed context for India's OSH Code. OISD-STD-105 is indexed only as a catalogue record until its authorized full text is provided.

## Data and Evaluation

```powershell
npm run sim:generate
npm run sim:evaluate
npm run test:backend
npm run rag:evaluate
```

The checked-in simulator output and evaluation are synthetic benchmarks, not observed incident data. `datasets/sensors/sensor_history.csv` has unknown provenance and is illustrative only. The CSB case-study corpus is real public incident material but has no synchronized sensor precursors, so it is not used for prediction evaluation. To test local permit suspension, set `ATLAS_ENABLE_PERMIT_ACTIONS=true` and call `POST /permits/evaluate` with `{"execute_suspensions": true}`. This changes only the local audited demo mirror, never an external permit system.

Regulatory document ingestion and source limits are documented in `datasets/regulations/README.md`.
Public incident source scope and selection bias are documented in `datasets/incidents/README.md`; sample sensor provenance is documented in `datasets/sensors/README.md`.

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
datasets            Illustrative snapshots, synthetic simulation, public cases, regulation sources
architecture        System diagrams and sequence flows
deployment          Deployment notes and local compose plan
```

## Not Connected Yet

- Live sensor/permit/CMMS sources, authentication, and a production-grade persistence service.
- Authorized full-text OISD-STD-105 and the current jurisdiction-specific implementing rules.
- An LLM answer-generation layer; copilot currently does intent routing and source-grounded deterministic responses.
- Field validation and independent safety-case approval of thresholds, model features, labels, and performance.

