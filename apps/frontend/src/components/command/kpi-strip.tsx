const kpis = [
  ["Current Risk", "86"],
  ["30 min Risk", "94"],
  ["Compliance", "65%"],
  ["Open Violations", "3"]
];

export function KpiStrip() {
  return (
    <section className="grid">
      {kpis.map(([label, value]) => (
        <div className="panel" key={label}>
          <p className="eyebrow">{label}</p>
          <strong className="metric-value">{value}</strong>
        </div>
      ))}
    </section>
  );
}
