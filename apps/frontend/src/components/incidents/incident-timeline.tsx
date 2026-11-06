"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Incident = { id: string; title: string; event_date: string; location: string; signals: string[]; outcome: string; lesson: string; source: string; source_url: string };
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
      <p className="eyebrow">Public case studies</p>
      <h1>Industrial incident learning</h1>
      <p className="panel">Official investigation summaries are external learning references, not incident records from this plant or predictive training labels.</p>
      {error && <p className="panel" role="alert">{error}</p>}
      {items.map((item) => <article className="panel" key={item.id}>
        <div className="panel-title"><h2>{item.title}</h2><strong>{item.event_date}</strong></div>
        <p>{item.location} · {item.event_date} · {item.signals.join(" / ")}</p>
        <p><strong>Outcome:</strong> {item.outcome}</p><p><strong>Learning:</strong> {item.lesson}</p>
        <a href={item.source_url} target="_blank" rel="noreferrer">{item.source} ({item.id})</a>
      </article>)}
      <section className="panel">
        <h2>Response recommendation</h2>
        {recommendation ? <><ul>{recommendation.actions.map((action) => <li key={action}>{action}</li>)}</ul><small>{recommendation.data_notice} No external action is executed.</small></> : <p>Build a recommendation from current sensor and permit evidence.</p>}
        <button className="button danger-button" onClick={() => void buildRecommendation()}>Generate recommendation</button>
      </section>
    </main>
  );
}
