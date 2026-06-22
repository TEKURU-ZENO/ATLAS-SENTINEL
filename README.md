# ATLAS Sentinel

Industrial Safety Intelligence Operating System for zero-harm operations.

ATLAS Sentinel turns fragmented plant signals into a living industrial digital twin that can detect compound hazards, explain why risk is rising, map violations to safety rules, and orchestrate preventive action before incidents occur.

## What Is Built

- Static demo at `index.html` for the fastest judge-ready walkthrough.
- Monorepo scaffold under `apps/` and `packages/` for the deployable product shape.
- Backend service skeleton with health, risk, twin, permit, compliance, incident, and copilot routes.
- Agent runtime skeleton for hazard correlation, permit intelligence, compliance, forecasting, emergency response, and copilot flows.
- Simulator seed data for the gas-rise + hot-work + shift-handover demo story.
- Shared risk engine, safety rules, and knowledge graph package starters.

## Demo Path

1. Open `index.html`.
2. Click `Inject Next Event` until the plant enters the compound hazard state.
3. Review the risk map, agent reasoning, compliance violations, and recommended action.
4. Trigger the emergency workflow.
5. Switch persona tabs for field safety, executive, and audit views.

## Monorepo Map

```text
apps/frontend       Next.js command center shell
apps/backend        FastAPI service boundary
apps/agent-runtime  LangGraph-ready multi-agent safety brain
apps/simulator      Digital twin event simulator
packages/*          Shared domain logic, rules, graph, UI, and types
datasets            Demo incidents, permits, sensors, regulations, and layout
architecture        System diagrams and sequence flows
deployment          Deployment notes and local compose plan
```

## MVP Build Order

1. Digital Twin Dashboard
2. Plant Heatmap
3. Risk Correlation Agent
4. Permit Intelligence Agent
5. Compliance Agent
6. Safety Copilot
7. Knowledge Graph Visualization
8. Emergency Response Workflow

