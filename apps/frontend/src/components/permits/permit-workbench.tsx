"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

type Evaluation = { permit_id: string; zone?: string; decision: string; rules: string[]; findings: { reason: string }[] };
type Result = { evaluations: Evaluation[]; suspended: string[]; executed: boolean; notice: string };

export function PermitWorkbench() {
  const [result, setResult] = useState<Result | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  const evaluate = useCallback(async (execute = false) => {
    setPending(true);
    setError("");
    try {
      setResult(await apiFetch<Result>("/permits/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ execute_suspensions: execute }),
      }));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Permit evaluation failed.");
    } finally {
      setPending(false);
    }
  }, []);

  useEffect(() => { void evaluate(); }, [evaluate]);
  const conflicts = result?.evaluations.filter((item) => item.decision === "suspend") ?? [];

  return (
    <main className="page">
      <p className="eyebrow">Permit Intelligence</p>
      <h1>Active work authorization</h1>
      <p>Each active permit is checked against the available sensor snapshot and configured demo rules.</p>
      {error && <div className="panel" role="alert">{error}</div>}
      <div className="panel">
        <button className="button primary-button" onClick={() => void evaluate()} disabled={pending}>{pending ? "Checking..." : "Re-evaluate permits"}</button>
      </div>
      {result?.evaluations.map((item) => (
        <article className="panel" key={item.permit_id}>
          <div className="panel-title"><h2>{item.permit_id}</h2><strong>{item.decision.toUpperCase()}</strong></div>
          <p>{item.zone ?? "Zone unavailable"} · Rules: {item.rules.length ? item.rules.join(", ") : "No conflict found"}</p>
          {item.findings.map((finding) => <p key={finding.reason}>{finding.reason}</p>)}
        </article>
      ))}
      {conflicts.length > 0 && !result?.executed && (
        <section className="panel">
          <label><input type="checkbox" checked={confirm} onChange={(event) => setConfirm(event.target.checked)} /> I intend to update the local demo permit mirror only.</label>
          <button className="button danger-button" disabled={!confirm || pending} onClick={() => { setConfirm(false); void evaluate(true); }}>Record suspension in demo mirror</button>
        </section>
      )}
      {result?.executed && <p className="panel" role="status">Suspended in local mirror: {result.suspended.join(", ") || "no permit changed"}</p>}
      <p className="panel">{result?.notice ?? "No permit evaluation loaded."} The gas limit is a prototype threshold, not an OISD clause or approved site limit.</p>
    </main>
  );
}
