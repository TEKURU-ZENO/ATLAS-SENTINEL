const zones = [
  { name: "Zone A", label: "Utilities", risk: 18, tone: "green" },
  { name: "Zone B", label: "Storage", risk: 24, tone: "green" },
  { name: "Zone C", label: "Boiler Island", risk: 86, tone: "red" },
  { name: "Zone D", label: "Compressor", risk: 35, tone: "yellow" },
  { name: "Zone E", label: "Loading Bay", risk: 57, tone: "orange" }
];

const signals = [
  ["Methane", "6.2% LEL", "up"],
  ["Hot Work Permit", "PTW-4421", "active"],
  ["Workers Exposed", "14", "live"],
  ["Forecast 30 min", "94", "critical"]
];

const reasoning = [
  "Methane Sensor C-04 is trending upward near Boiler 7.",
  "Hot work permit PTW-4421 overlaps with active maintenance in Zone C.",
  "Shift handover is in progress, reducing command continuity.",
  "Three historical incidents share the same compound pattern."
];

const actions = [
  "Suspend hot work permit PTW-4421",
  "Evacuate workers from Zone C",
  "Dispatch emergency response team",
  "Seal evidence package for audit"
];

export default function HomePage() {
  return (
    <main className="dashboard">
      <section className="hero-command">
        <div className="hero-copy">
          <p className="eyebrow">Industrial Safety Intelligence Operating System</p>
          <h1>Compound hazard intelligence for zero-harm operations.</h1>
          <p className="hero-text">
            ATLAS Sentinel fuses plant state, worker exposure, permits, maintenance, and compliance into one living command surface.
          </p>
          <div className="hero-actions">
            <a className="button primary-button" href="/command-center">Open command center</a>
            <a className="button ghost-button" href="/copilot">Ask Safety Copilot</a>
          </div>
        </div>
        <div className="risk-orbit" aria-label="Critical risk summary">
          <span>Current risk</span>
          <strong>86</strong>
          <small>Critical in Zone C</small>
        </div>
      </section>

      <section className="kpi-row" aria-label="Live signal summary">
        {signals.map(([label, value, state]) => (
          <article className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{state}</small>
          </article>
        ))}
      </section>

      <section className="ops-grid">
        <article className="command-panel twin-panel">
          <div className="panel-title">
            <div>
              <p className="eyebrow">Geospatial Safety Analytics</p>
              <h2>Plant digital twin</h2>
            </div>
            <span className="critical-chip">Compound hazard</span>
          </div>
          <div className="plant-map">
            {zones.map((zone) => (
              <div className={`zone-tile ${zone.tone}`} key={zone.name}>
                <strong>{zone.name}</strong>
                <span>{zone.label}</span>
                <small>Risk {zone.risk}</small>
              </div>
            ))}
            <div className="pipe horizontal" />
            <div className="pipe vertical" />
          </div>
        </article>

        <article className="command-panel">
          <div className="panel-title">
            <div>
              <p className="eyebrow">Agentic Safety Orchestration</p>
              <h2>Why ATLAS escalated</h2>
            </div>
          </div>
          <ol className="reasoning-feed">
            {reasoning.map((item) => <li key={item}>{item}</li>)}
          </ol>
        </article>

        <article className="command-panel action-panel">
          <div>
            <p className="eyebrow">Emergency Commander Agent</p>
            <h2>Preventive workflow</h2>
          </div>
          <ul className="action-list">
            {actions.map((action) => <li key={action}>{action}</li>)}
          </ul>
          <a className="button danger-button" href="/incidents">Generate evidence package</a>
        </article>
      </section>

      <section className="persona-strip">
        <article>
          <span>Control Room</span>
          <strong>One-screen risk, forecast, and action queue.</strong>
        </article>
        <article>
          <span>Field Safety</span>
          <strong>Permit-aware copilot for work authorization.</strong>
        </article>
        <article>
          <span>Compliance</span>
          <strong>Evidence bundle with regulation references.</strong>
        </article>
        <article>
          <span>Plant Head</span>
          <strong>Risk index, violations, and near-miss trend.</strong>
        </article>
      </section>
    </main>
  );
}
