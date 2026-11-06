"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Finding = { permit_id: string; rule_id: string; finding: string; action: string; legal_conclusion: boolean };
type Compliance = { findings: Finding[]; risk_review: { required: boolean; score: number; legal_references: string[] }; notice: string };
type Source = { document?: string; section?: string; page?: number | null; source_url?: string; text: string; score: number };

export function ComplianceWorkbench() {
  const [report, setReport] = useState<Compliance | null>(null);
  const [query, setQuery] = useState("What must an employer do about workplace hazards?");
  const [sources, setSources] = useState<Source[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Compliance>("/compliance/findings").then(setReport).catch((cause) => setError(cause instanceof Error ? cause.message : "Compliance report unavailable."));
  }, []);

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    try {
      const result = await apiFetch<{ results: Source[] }>(`/compliance/search?q=${encodeURIComponent(query)}`);
      setSources(result.results);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Regulation search failed.");
    }
  }

  return (
    <main className="page">
      <p className="eyebrow">Compliance review</p>
      <h1>Findings and source text</h1>
      {error && <p className="panel" role="alert">{error}</p>}
      <section className="panel">
        <h2>Operational checks</h2>
        {report?.findings.length ? report.findings.map((finding) => <article key={`${finding.permit_id}-${finding.rule_id}`}>
          <strong>{finding.rule_id} · {finding.permit_id}</strong><p>{finding.finding}</p><p>{finding.action}</p>
        </article>) : <p>{report ? "No permit-rule findings in the current data snapshot." : "Loading findings..."}</p>}
        {report && <p>Compound-risk review: {report.risk_review.required ? `required (${report.risk_review.score}/99)` : `not triggered (${report.risk_review.score}/99)`}</p>}
        <small>{report?.notice ?? "Operational rule output; not a legal compliance determination."}</small>
      </section>
      <section className="compliance-search">
        <h2>Regulation retrieval</h2>
        <form onSubmit={search}>
          <label htmlFor="regulation-query">Search source passages</label>
          <div className="copilot-input-row"><input id="regulation-query" value={query} onChange={(event) => setQuery(event.target.value)} /><button className="button primary-button" type="submit">Search</button></div>
        </form>
        {sources.map((source) => <article className="regulation-result" key={`${source.document}-${source.section}`}>
          <h3>{source.source_url ? <a href={source.source_url} target="_blank" rel="noreferrer">{source.document}</a> : source.document}</h3>
          <p>{source.section}{source.page ? ` · p. ${source.page}` : ""} · relevance {source.score}</p>
          <p>{source.text}</p>
        </article>)}
      </section>
    </main>
  );
}
