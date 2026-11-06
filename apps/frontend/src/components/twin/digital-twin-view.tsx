"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type TwinState = {
  zone: string;
  equipment: string;
  methane_percent_lel: number;
  sensor_id: string;
  sensor_timestamp: string;
  sensor_history: { timestamp: string; value: number; unit: string }[];
  active_hot_work: boolean;
  maintenance_active: boolean | null;
  shift_handover: boolean | null;
  workers: number | null;
  permit_id: string | null;
  data_notice: string;
};

export function DigitalTwinView() {
  const [state, setState] = useState<TwinState | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<TwinState>("/twin/state").then(setState).catch((cause) => setError(cause instanceof Error ? cause.message : "Digital twin unavailable.")); }, []);

  return (
    <main className="page">
      <p className="eyebrow">Digital twin snapshot</p>
      <h1>{state?.zone ?? "Plant state"}</h1>
      {error && <p className="panel" role="alert">{error}</p>}
      <section className="grid">
        <article className="panel"><p className="eyebrow">Equipment</p><h2>{state?.equipment ?? "--"}</h2><p>Sensor {state?.sensor_id ?? "--"}</p><strong>{state ? `${state.methane_percent_lel.toFixed(1)}% LEL` : "--"}</strong></article>
        <article className="panel"><p className="eyebrow">Work authorization</p><h2>{state?.permit_id ?? "No active permit"}</h2><p>Hot work: {state ? state.active_hot_work ? "active" : "not recorded" : "--"}</p></article>
        <article className="panel"><p className="eyebrow">Unobserved state</p><h2>Not provided</h2><p>Workers: {state?.workers ?? "unknown"} · Maintenance: {state?.maintenance_active ?? "unknown"} · Handover: {state?.shift_handover ?? "unknown"}</p></article>
      </section>
      <section className="panel">
        <h2>Sensor history</h2>
        <div className="table-scroll"><table><thead><tr><th>Timestamp</th><th>Sensor</th><th>Reading</th></tr></thead>
          <tbody>{(state?.sensor_history ?? []).map((reading, index) => <tr key={`${reading.timestamp}-${index}`}><td>{new Date(reading.timestamp).toLocaleString()}</td><td>{state?.sensor_id ?? "--"}</td><td>{reading.value.toFixed(1)}% LEL</td></tr>)}</tbody>
        </table></div>
      </section>
      <p className="panel">{state?.data_notice ?? "Loading repository sensor records..."}</p>
    </main>
  );
}
