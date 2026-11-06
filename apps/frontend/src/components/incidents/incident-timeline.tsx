"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Incident = { id: string; zone: string; signals: string[]; outcome: string; lesson: string };
type Recommendation = { workflow: string; executed: boolean; actions: string[]; data_notice: string };

export function IncidentTimeline() {
  const [items, setItems] = useState<Incident[]>([]);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<{ items: Incident[] }>("/incidents").then((result) => setItems(result.items)).catch((cause) => setError(cause instanceof Error ? cause.message : "Incident records unavailable.")); }, []);
  async function buildRecommendation() {
    try { setRecommendation(await apiFetch<Recommendation>("/incidents/emergency-workflow", { method: "POST" })); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Response recommendation unavailable."); }
  }

  return (
    <main className="page">
      <p className="eyebrow">Incident learning</p>
      <h1>Recorded near misses and lessons</h1>
      {error && <p className="panel" role="alert">{error}</p>}
      {items.map((item) => <article className="panel" key={item.id}>
        <div className="panel-title"><h2>{item.id}</h2><strong>{item.outcome.replaceAll("_", " ")}</strong></div>
        <p>{item.zone} · {item.signals.join(" / ")}</p><p>{item.lesson}</p>
      </article>)}
      <section className="panel">
        <h2>Response recommendation</h2>
        {recommendation ? <><ul>{recommendation.actions.map((action) => <li key={action}>{action}</li>)}</ul><small>{recommendation.data_notice} No external action is executed.</small></> : <p>Build a recommendation from current sensor and permit evidence.</p>}
        <button className="button danger-button" onClick={() => void buildRecommendation()}>Generate recommendation</button>
      </section>
    </main>
  );
}
