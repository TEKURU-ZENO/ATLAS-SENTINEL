"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";

export function Topbar() {
  const [summary, setSummary] = useState<{ zone: string; current: number } | null>(null);
  useEffect(() => {
    Promise.all([apiFetch<{ zone: string }>("/twin/state"), apiFetch<{ current: number }>("/risks/current")])
      .then(([twin, risk]) => setSummary({ zone: twin.zone, current: risk.current }))
      .catch(() => setSummary(null));
  }, []);
  return (
    <header className="topbar">
      <div><p className="eyebrow">Snapshot-based prototype</p><h1>Operations workspace</h1></div>
      <div className="topbar-actions"><span className={`live-pill ${summary ? "connected" : "disconnected"}`}>{summary ? "API connected" : "API unavailable"}</span><strong>{summary ? `${summary.zone} risk: ${summary.current}` : "No live plant connection"}</strong></div>
    </header>
  );
}
