"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Metrics = { precision: number; recall: number; false_alarms_per_1000_windows: number; false_alarms_per_zone_day: number; incident_lead_coverage: string; median_lead_minutes: number | null };
type Evaluation = { target: string; model: { name: string; metrics: Metrics }; rules_baseline: { threshold_sweep: Record<string, Metrics> }; caveat: string };

export default function AnalyticsPage() {
  const [data, setData] = useState<Evaluation | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<Evaluation>("/risks/evaluation").then(setData).catch((cause) => setError(cause instanceof Error ? cause.message : "Evaluation report unavailable.")); }, []);
  const metrics = data?.model.metrics;
  return (
    <main className="page">
      <p className="eyebrow">Model evaluation</p>
      <h1>30 to 60 minute precursor benchmark</h1>
      {error && <p className="panel" role="alert">{error}</p>}
      {metrics && <>
        <section className="kpi-row">
          <article className="metric-card"><span>Model precision</span><strong>{(metrics.precision * 100).toFixed(1)}%</strong><small>Chronological holdout</small></article>
          <article className="metric-card"><span>Recall</span><strong>{(metrics.recall * 100).toFixed(1)}%</strong><small>Incident windows</small></article>
          <article className="metric-card"><span>False alarms</span><strong>{metrics.false_alarms_per_1000_windows}</strong><small>Per 1,000 windows</small></article>
          <article className="metric-card"><span>Median lead</span><strong>{metrics.median_lead_minutes ?? "--"} min</strong><small>{metrics.incident_lead_coverage} holdout events covered</small></article>
        </section>
        <section className="panel">
          <h2>{data?.model.name} vs compound-rule thresholds</h2>
          <div className="table-scroll"><table><thead><tr><th>Method</th><th>Precision</th><th>Recall</th><th>False alarms / 1,000</th><th>Lead coverage</th></tr></thead><tbody>
            <tr><td>Gradient boosting</td><td>{(metrics.precision * 100).toFixed(1)}%</td><td>{(metrics.recall * 100).toFixed(1)}%</td><td>{metrics.false_alarms_per_1000_windows}</td><td>{metrics.incident_lead_coverage}</td></tr>
            {Object.entries(data?.rules_baseline.threshold_sweep ?? {}).map(([threshold, result]) => <tr key={threshold}><td>Rules ≥ {threshold}</td><td>{(result.precision * 100).toFixed(1)}%</td><td>{(result.recall * 100).toFixed(1)}%</td><td>{result.false_alarms_per_1000_windows}</td><td>{result.incident_lead_coverage}</td></tr>)}
          </tbody></table></div>
        </section>
      </>}
      <p className="panel">{data?.caveat ?? "Loading simulator evaluation..."} Metrics only assess the synthetic event generator and must not be read as plant performance.</p>
    </main>
  );
}
