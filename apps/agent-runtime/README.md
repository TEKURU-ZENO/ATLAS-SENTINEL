# Agent Runtime

LangGraph-ready safety brain for ATLAS Sentinel.

The current scaffold runs the MVP reasoning path:

1. Hazard Correlation Agent scores compound risk.
2. Permit Intelligence Agent suspends conflicting hot work.
3. Compliance Agent maps violations.
4. Forecasting Agent projects risk.
5. Emergency Commander Agent recommends response actions.

Smoke test:

```bash
python -c "from agents.graph import run_agent_graph; print(run_agent_graph({'zone':'Zone C','methane_percent_lel':6.2,'active_hot_work':True,'maintenance_active':True,'shift_handover':True,'workers':14}))"
```
