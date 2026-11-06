"use client";

import { FormEvent, useState } from "react";
import { apiFetch } from "../../services/api";

type CopilotResult = {
  answer: string;
  recommendation: string;
  citations: { source: string; detail: string; url?: string; page?: number | null }[];
  data_source: string;
  data_notice: string;
};

export function ChatWindow() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<CopilotResult | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim() || pending) return;
    setPending(true);
    setError("");
    try {
      const data = await apiFetch<CopilotResult>("/copilot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      });
      setResult(data);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not reach the safety API.");
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="page">
      <p className="eyebrow">Safety Copilot</p>
      <h1>Ask about site conditions</h1>
      <form className="panel" onSubmit={submit}>
        <label htmlFor="copilot-question">Question</label>
        <div className="copilot-input-row">
          <input
            id="copilot-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about permits, risk, gas readings, or past incidents"
            required
          />
          <button type="submit" disabled={pending || !question.trim()}>{pending ? "Checking..." : "Ask"}</button>
        </div>
        {error && <p role="alert">{error}</p>}
      </form>
      {result && (
        <section className="panel" aria-live="polite">
          <p><strong>Assessment</strong></p>
          <p>{result.answer}</p>
          <p><strong>Recommended next step:</strong> {result.recommendation}</p>
          <p className="eyebrow">Evidence</p>
          <ul>{result.citations.map((citation) => <li key={citation.source}>
            <strong>{citation.url ? <a href={citation.url} target="_blank" rel="noreferrer">{citation.source}</a> : citation.source}</strong>
            {citation.page ? ` (PDF p. ${citation.page})` : ""}: {citation.detail}
          </li>)}</ul>
          <small>{result.data_notice} Verify against live site systems before operational decisions.</small>
        </section>
      )}
    </main>
  );
}
