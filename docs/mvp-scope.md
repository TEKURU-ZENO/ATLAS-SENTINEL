# Current Prototype Scope

## Implemented

- Reproducible, seeded multi-zone synthetic streams with permits, shifts, maintenance periods, occupancy, and 30-60-minute precursor labels.
- Explainable compound-risk rules baseline and an offline gradient-boosting evaluation on a chronological holdout.
- Permit checks for gas conflict, missing sensor state, confined-space gas-test evidence, and expiry. Local suspension writes an SQLite status transition and audit row behind an explicit environment gate.
- TF-IDF/lexical regulation retrieval, PDF ingestion with section/page metadata, and a 50-question retrieval/citation benchmark.
- API-backed Next.js screens for dashboard, twin, permits, compliance, incidents, analytics, and copilot.

## Deliberate Limits

- Simulator labels and all reported model metrics are synthetic and cannot establish field precision or false-alarm performance.
- Current operational API values come from repository snapshots, not live sensors or work systems. Unknown maintenance, worker, and shift state stays unknown.
- The 2.5% LEL hot-work interlock is a demo assumption, not a quoted legal threshold.
- No external permit action, PLC command, evacuation, or emergency response is executed.
- Current-Code retrieval contains curated source summaries; the authorized OISD-STD-105 full text and jurisdiction-specific implementing rules are not ingested.
- Copilot is deterministic intent routing plus cited retrieval, not a generative model.
