# Plant Simulator

Generate a deterministic synthetic dataset with 21 days, three zones, 10-minute gas/temperature observations, hot-work permit windows, maintenance work orders, shifts, worker occupancy, and injected incident precursors. The injected set mixes combustible-gas ramps, work-control conflicts, and incidents with no observable modeled precursor; unrelated nuisance gas excursions are included to test false alarms.

```powershell
python apps/simulator/generate_dataset.py --days 21 --seed 20261106
python apps/simulator/evaluate_risk.py
```

The generator writes `datasets/simulated/`. Change the seed or day count to produce another run. Evaluation explicitly joins `sensor_stream.csv` to `incident_windows.csv` on timestamp and zone, failing if keys are missing or duplicated. It reports two complementary checks:

- The full dataset scores the shared `packages/risk-engine/compound_risk.py` implementation at a fixed score threshold of 45 against a methane-only alarm at 1.0% LEL. The report includes window precision, false-alarm rate among negative windows, per-event lead time, and alert episodes. False alarms per zone-day count episodes with no overlap with any positive window; window false alarms are reported separately because these two quantities answer different operational questions.
- A chronological 75/25 split with a 60-minute purge trains a histogram gradient-boosting classifier and compares it to the compound-rule baseline at several thresholds. The model threshold is fixed before evaluation.

Current checked-in synthetic run: compound risk at score >=45 has 72.41% window precision, 0.09% false-alarm rate, and 0.88 false-positive windows per 1,000; it detects 10/21 events with 40-minute median lead. Coverage is 8/8 work-control conflicts, 2/8 combustible-gas ramps, and 0/5 deliberately unobserved precursors. The 1.0% LEL methane-only baseline has 16.67% precision, 0.89% false-alarm rate, and 8.82 false-positive windows per 1,000; it detects 8/21 events with 40-minute median lead. Episode false-alarm burden is 0.00 vs 0.38 per zone-day, respectively. This only shows the fixed compound rule is better suited to this particular injected work-overlap scenario; it does not establish operational performance.

The learned classifier on the single chronological holdout has 100% window precision but only 16.67% recall and covers 3/6 holdout events. That is a high miss rate despite zero false-positive windows; a single synthetic split is not evidence of reliable forecasting.

All observations and outcomes are synthetic and intentionally constructed. The full-stream rule results are descriptive, not an independent test set. The learned-model score is a single chronological holdout within one simulator configuration and seed. Neither estimates real plant performance or authorizes safety actions. Window-level precision and false-alarm rates count adjacent alert windows separately; event lead coverage is reported separately to show incident-level detection.
