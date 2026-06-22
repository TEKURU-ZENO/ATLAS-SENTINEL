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
          <strong style={{ fontSize: 34 }}>{value}</strong>
        </div>
      ))}
    </section>
  );
}
