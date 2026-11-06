# Agent Runtime

The current synchronous graph shares the compound-risk and permit-rule packages with the FastAPI backend. It produces risk drivers, permit decisions, compliance review notes, and response recommendations. It does not emit a forecast; prediction is an offline research evaluation only.

The graph does not call external systems. A permit `suspend` result is an evaluation; persistence is available only through the backend's explicitly enabled local demo mirror. The learned classifier is evaluated offline by `apps/simulator/evaluate_risk.py` and is not treated as a live safety predictor.

Smoke test from the repository root:

```powershell
python -c "import sys; sys.path.insert(0, 'apps/agent-runtime'); from agents.graph import run_agent_graph; print(run_agent_graph({'zone':'Zone C','permit_id':'PTW-4421','methane_percent_lel':6.2,'active_hot_work':True,'maintenance_active':True,'shift_handover':True}))"
```
