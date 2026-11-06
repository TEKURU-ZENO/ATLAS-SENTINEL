# Plant Simulator

Generate a deterministic synthetic dataset with 21 days, three zones, 10-minute gas/temperature observations, hot-work permit windows, maintenance work orders, shifts, worker occupancy, and injected incident precursors.

```powershell
python apps/simulator/generate_dataset.py --days 21 --seed 20261106
python apps/simulator/evaluate_risk.py
```

The generator writes `datasets/simulated/`. Change the seed or day count to produce another run. The evaluation uses a chronological 75/25 split with a 60-minute purge, trains a histogram gradient-boosting classifier, and reports precision, recall, false alarms per 1,000 windows and zone-day, event lead coverage, and median lead time against the compound-rule baseline at several thresholds. The model threshold is fixed before evaluation.

All observations and outcomes are synthetic and intentionally constructed. The benchmark is useful for testing data pipelines and code paths only; it does not estimate real plant performance or authorize safety actions.
