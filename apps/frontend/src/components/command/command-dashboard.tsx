"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Risk = {
  current: number | null;
  snapshot_score: number | null;
  status: "available" | "stale" | "unavailable" | "unverified";
  sensor_trend: "rising" | "falling" | "stable" | "unknown";
  sensor_delta: number | null;
  level: string;
  reason: string;
  drivers: { label: string; points: number }[];
  interactions: { label: string; points: number }[];
  data_notice: string;
  sensor_timestamp: string | null;
  sensor_stale: boolean;
  sensor_verified: boolean;
  sensor_age_minutes: number | null;
};
type Twin = {
  zone: string;
  equipment: string;
  methane_percent_lel: number | null;
  sensor_id: string | null;
  sensor_timestamp: string | null;
  sensor_stale: boolean;
  sensor_verified: boolean;
  sensor_age_minutes: number | null;
  sensor_history: { timestamp: string; value: number }[];
  permit_id: string | null;
  active_hot_work: boolean;
  workers: number | null;
  data_notice: string;
};
type Permit = { decision: string; permit: string | null; evaluations: { permit_id: string; decision: string; rules: string[]; findings: { reason: string }[] }[] };
type Workflow = { workflow: string; actions: string[]; executed: boolean };

function formatSampleAge(minutes: number | null): string {
  if (minutes == null) return "age unknown";
  return minutes >= 1440 ? `${Math.floor(minutes / 1440)} days old` : `${Math.round(minutes)} minutes old`;
}

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
        <div className={`risk-orbit ${risk && risk.status !== "available" ? "stale" : ""}`} aria-label={risk && risk.status !== "available" ? "Current compound risk unavailable because sensor data is stale, unverified, or missing" : "Current compound risk score"}>
          <span>{risk?.status === "stale" ? "Current risk unavailable" : risk?.status === "unavailable" ? "No sensor data" : risk?.status === "unverified" ? "Sensor source unverified" : "Compound risk snapshot"}</span>
          <strong>{risk?.current ?? "--"}</strong>
          <small>{risk ? risk.level : loading ? "Loading" : "API unavailable"}</small>
        </div>
      </section>

      {error && <p className="panel" role="alert">{error}</p>}
      <section className="kpi-row" aria-label="Operational snapshot">
        <article className="metric-card"><span>Gas reading</span><strong>{twin?.methane_percent_lel == null ? "--" : `${twin.methane_percent_lel.toFixed(1)}%`}</strong><small className={twin && (twin.sensor_stale || !twin.sensor_verified) ? "stale-notice" : undefined}>{twin?.sensor_id ?? "No sensor data"} · {twin?.sensor_stale ? `stale · ${formatSampleAge(twin.sensor_age_minutes)}` : twin && !twin.sensor_verified ? "unverified sample" : "% LEL"}</small></article>
        <article className="metric-card"><span>Permit check</span><strong>{permits?.decision ?? "--"}</strong><small>{permits?.permit ?? "No active permit"}</small></article>
        <article className="metric-card"><span>Recent gas trend</span><strong>{risk?.sensor_trend ?? "--"}</strong><small>{risk?.sensor_delta == null ? "Insufficient samples" : `${risk.sensor_delta > 0 ? "+" : ""}${risk.sensor_delta.toFixed(2)}% LEL since prior sample`}</small></article>
        <article className="metric-card"><span>Incident forecast</span><strong>Unavailable</strong><small>No field-validated forecast model</small></article>
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
          {risk && risk.status !== "available" ? <p>{risk.status === "stale" ? `Current drivers are withheld because the sensor sample is stale. Last recorded snapshot score: ${risk.snapshot_score ?? "--"}/99.` : risk.status === "unverified" ? "Current drivers are withheld because the sensor source is unverified." : "Current drivers are withheld because no sensor sample is available."}</p> : risk ? <ol className="reasoning-feed">{[...risk.drivers, ...risk.interactions].map((item) => <li key={item.label}>{item.label}<strong> +{item.points}</strong></li>)}</ol> : <p>{loading ? "Loading risk factors..." : "No risk data available."}</p>}
          {risk && <small>{risk.reason}</small>}
        </article>

        <article className="command-panel action-panel">
          <div><p className="eyebrow">Response workflow</p><h2>Site review</h2></div>
          {workflow ? <ul className="action-list">{workflow.actions.map((action) => <li key={action}>{action}</li>)}</ul> : <p>Generate an evidence-based response recommendation from current risk and permit checks.</p>}
          <button className="button danger-button" onClick={() => void recommendResponse()}>Generate recommendation</button>
        </article>
      </section>
      <p className="panel">{twin?.data_notice ?? "No operational snapshot loaded."} The risk score is a prototype current-state rule; verify all conditions through live site systems and approved procedures.</p>
    </main>
  );
}
