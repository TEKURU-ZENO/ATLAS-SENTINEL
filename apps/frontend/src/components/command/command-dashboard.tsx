"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Risk = {
  current: number;
  forecast30: number;
  forecast60: number;
  level: string;
  reason: string;
  drivers: { label: string; points: number }[];
  interactions: { label: string; points: number }[];
  data_notice: string;
  sensor_timestamp: string;
};
type Twin = {
  zone: string;
  equipment: string;
  methane_percent_lel: number;
  sensor_id: string;
  sensor_timestamp: string;
  sensor_history: { timestamp: string; value: number }[];
  permit_id: string | null;
  active_hot_work: boolean;
  workers: number | null;
  data_notice: string;
};
type Permit = { decision: string; permit: string | null; evaluations: { permit_id: string; decision: string; rules: string[]; findings: { reason: string }[] }[] };
type Workflow = { workflow: string; actions: string[]; executed: boolean };

export function CommandDashboard() {
  const [snapshot, setSnapshot] = useState<{ risk: Risk; twin: Twin; permits: Permit } | null>(null);
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [risk, twin, permits] = await Promise.all([
        apiFetch<Risk>("/risks/current"),
        apiFetch<Twin>("/twin/state"),
        apiFetch<Permit>("/permits/validate"),
      ]);
      setSnapshot({ risk, twin, permits });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load the ATLAS API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  async function recommendResponse() {
    try {
      setWorkflow(await apiFetch<Workflow>("/incidents/emergency-workflow", { method: "POST" }));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not generate response recommendations.");
    }
  }

  const { risk, twin, permits } = snapshot ?? {};
  return (
    <main className="dashboard">
      <section className="hero-command">
        <div className="hero-copy">
          <p className="eyebrow">Operations overview</p>
          <h1>Plant safety, grounded in recorded evidence.</h1>
          <p className="hero-text">Risk drivers, permit checks, and response recommendations from the configured ATLAS API.</p>
          <div className="hero-actions">
            <button className="button primary-button" onClick={() => void refresh()} disabled={loading}>{loading ? "Refreshing..." : "Refresh snapshot"}</button>
            <a className="button ghost-button" href="/copilot">Ask Safety Copilot</a>
          </div>
        </div>
        <div className="risk-orbit" aria-label="Current compound risk score">
          <span>Compound risk</span>
          <strong>{risk?.current ?? "--"}</strong>
          <small>{risk ? risk.level : loading ? "Loading" : "API unavailable"}</small>
        </div>
      </section>

      {error && <p className="panel" role="alert">{error}</p>}
      <section className="kpi-row" aria-label="Operational snapshot">
        <article className="metric-card"><span>Gas reading</span><strong>{twin ? `${twin.methane_percent_lel.toFixed(1)}%` : "--"}</strong><small>{twin?.sensor_id ?? "No sensor data"} · % LEL</small></article>
        <article className="metric-card"><span>Permit check</span><strong>{permits?.decision ?? "--"}</strong><small>{permits?.permit ?? "No active permit"}</small></article>
        <article className="metric-card"><span>30 min risk</span><strong>{risk?.forecast30 ?? "--"}</strong><small>Rule-based trend projection</small></article>
        <article className="metric-card"><span>60 min risk</span><strong>{risk?.forecast60 ?? "--"}</strong><small>Rule-based trend projection</small></article>
      </section>

      <section className="ops-grid">
        <article className="command-panel twin-panel">
          <div className="panel-title"><div><p className="eyebrow">Digital twin snapshot</p><h2>{twin?.zone ?? "Plant zone"}</h2></div><span className="critical-chip">{twin?.equipment ?? "Awaiting data"}</span></div>
          <div className="plant-map">
            <div className={`zone-tile ${risk?.current && risk.current >= 60 ? "red" : "green"}`}>
              <strong>{twin?.zone ?? "--"}</strong><span>{twin?.equipment ?? "Equipment unavailable"}</span>
              <small>{twin?.active_hot_work ? `Hot work active · ${twin.permit_id}` : "No active hot work recorded"}</small>
            </div>
            <div className="zone-tile"><strong>{twin?.workers ?? "Unknown"}</strong><span>Workers</span><small>Not recorded in source snapshot</small></div>
          </div>
          <small>Sensor time: {twin?.sensor_timestamp ? new Date(twin.sensor_timestamp).toLocaleString() : "--"}</small>
        </article>

        <article className="command-panel">
          <div className="panel-title"><div><p className="eyebrow">Explainable model</p><h2>Risk drivers</h2></div></div>
          {risk ? <ol className="reasoning-feed">{[...risk.drivers, ...risk.interactions].map((item) => <li key={item.label}>{item.label}<strong> +{item.points}</strong></li>)}</ol> : <p>{loading ? "Loading risk factors..." : "No risk data available."}</p>}
          {risk && <small>{risk.reason}</small>}
        </article>

        <article className="command-panel action-panel">
          <div><p className="eyebrow">Response workflow</p><h2>Site review</h2></div>
          {workflow ? <ul className="action-list">{workflow.actions.map((action) => <li key={action}>{action}</li>)}</ul> : <p>Generate an evidence-based response recommendation from current risk and permit checks.</p>}
          <button className="button danger-button" onClick={() => void recommendResponse()}>Generate recommendation</button>
        </article>
      </section>
      <p className="panel">{twin?.data_notice ?? "No operational snapshot loaded."} Forecasts and permit rules are prototypes; verify all conditions through live site systems and approved procedures.</p>
    </main>
  );
}
