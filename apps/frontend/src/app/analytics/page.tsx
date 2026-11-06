"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Metrics = { precision: number; recall: number; false_alarm_rate: number; false_alarms_per_1000_windows: number; false_alarms_per_zone_day: number; false_alarm_windows_per_zone_day: number; alert_episodes: number; false_alarm_episodes: number; episode_precision: number; incident_lead_coverage: string; median_lead_minutes: number | null };
type IncidentLead = { incident_id: string; zone: string; timestamp: string; detected: boolean; lead_minutes: number | null };
type DirectMetrics = Metrics & { incident_lead_times: IncidentLead[] };
type Evaluation = {
  target: string;
  model: { name: string; metrics: Metrics };
  rules_baseline: { threshold_sweep: Record<string, Metrics> };
  ground_truth_compound_risk: {
    labeled_windows: number;
    positive_windows: number;
    compound_incident_coverage_by_mechanism: Record<string, { detected: number; total: number; coverage: string }>;
    compound_risk: { alarm_threshold: number; metrics: DirectMetrics };
    methane_only_baseline: { alarm_rule: string; metrics: DirectMetrics };
  };
  caveat: string;
};

export default function AnalyticsPage() {
  const [data, setData] = useState<Evaluation | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<Evaluation>("/risks/evaluation").then(setData).catch((cause) => setError(cause instanceof Error ? cause.message : "Evaluation report unavailable.")); }, []);
  const metrics = data?.model.metrics;
  const direct = data?.ground_truth_compound_risk;
  const compound = direct?.compound_risk.metrics;
  const methane = direct?.methane_only_baseline.metrics;
  const maxFalseAlarms = Math.max(compound?.false_alarms_per_1000_windows ?? 0, methane?.false_alarms_per_1000_windows ?? 0, 1);
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
        {direct && compound && methane && <>
          <section className="panel">
            <p className="eyebrow">Direct label evaluation · {direct.labeled_windows.toLocaleString()} joined windows · {direct.positive_windows} positive</p>
            <h2>Compound risk vs methane-only alarm</h2>
            <div className="alarm-chart" role="img" aria-label={`False alarms per 1,000 windows: compound risk ${compound.false_alarms_per_1000_windows}, methane-only ${methane.false_alarms_per_1000_windows}`}>
              {[{ label: `Compound risk ≥ ${direct.compound_risk.alarm_threshold}`, value: compound.false_alarms_per_1000_windows, color: "compound" }, { label: direct.methane_only_baseline.alarm_rule, value: methane.false_alarms_per_1000_windows, color: "methane" }].map((bar) => <div className="alarm-chart-row" key={bar.label}>
                <span>{bar.label}</span><div className="alarm-track"><div className={`alarm-bar ${bar.color}`} style={{ width: `${Math.max(2, bar.value / maxFalseAlarms * 100)}%` }} /></div><strong>{bar.value}</strong>
              </div>)}
              <small>False-positive windows per 1,000 total windows</small>
            </div>
            <div className="table-scroll"><table><thead><tr><th>Method</th><th>Window precision</th><th>Window false-alarm rate</th><th>False windows / 1,000</th><th>False alert episodes / zone-day</th><th>Incident coverage</th><th>Median lead</th></tr></thead><tbody>
              <tr><td>Compound risk ≥ {direct.compound_risk.alarm_threshold}</td><td>{(compound.precision * 100).toFixed(1)}%</td><td>{(compound.false_alarm_rate * 100).toFixed(2)}%</td><td>{compound.false_alarms_per_1000_windows}</td><td>{compound.false_alarms_per_zone_day}</td><td>{compound.incident_lead_coverage}</td><td>{compound.median_lead_minutes ?? "--"} min</td></tr>
              <tr><td>{direct.methane_only_baseline.alarm_rule}</td><td>{(methane.precision * 100).toFixed(1)}%</td><td>{(methane.false_alarm_rate * 100).toFixed(2)}%</td><td>{methane.false_alarms_per_1000_windows}</td><td>{methane.false_alarms_per_zone_day}</td><td>{methane.incident_lead_coverage}</td><td>{methane.median_lead_minutes ?? "--"} min</td></tr>
            </tbody></table></div>
            <small>Window false alarms count each negative 10-minute prediction. Alert-episode rates merge consecutive predicted windows and count only episodes with no precursor-label overlap.</small>
            <small>This full-stream fixed-rule comparison is descriptive, not an independent test set. Use it to inspect behavior, not to claim field validation.</small>
          </section>
          <section className="panel">
            <h2>Lead time by injected incident</h2>
            <div className="table-scroll"><table><thead><tr><th>Incident</th><th>Zone</th><th>Event time (UTC)</th><th>Compound risk</th><th>Methane-only</th></tr></thead><tbody>
              {compound.incident_lead_times.map((event, index) => {
                const methaneEvent = methane.incident_lead_times[index];
                const leadLabel = (item?: IncidentLead) => item?.lead_minutes == null ? "Not detected" : `${item.lead_minutes} min`;
                return <tr key={event.incident_id}><td>{event.incident_id}</td><td>{event.zone}</td><td>{new Date(event.timestamp).toLocaleString("en-GB", { timeZone: "UTC", timeZoneName: "short" })}</td><td>{leadLabel(event)}</td><td>{leadLabel(methaneEvent)}</td></tr>;
              })}
            </tbody></table></div>
          </section>
          <section className="panel">
            <h2>Compound-rule coverage by precursor type</h2>
            <div className="table-scroll"><table><thead><tr><th>Injected mechanism</th><th>Detected</th><th>Total</th><th>Coverage</th></tr></thead><tbody>
              {Object.entries(direct.compound_incident_coverage_by_mechanism).map(([mechanism, result]) => <tr key={mechanism}><td>{mechanism.replaceAll("_", " ")}</td><td>{result.detected}</td><td>{result.total}</td><td>{result.coverage}</td></tr>)}
            </tbody></table></div>
          </section>
        </>}
      </>}
      <p className="panel">{data?.caveat ?? "Loading simulator evaluation..."} Metrics only assess the synthetic event generator and must not be read as plant performance.</p>
    </main>
  );
}
