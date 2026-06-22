export function PlantMap() {
  return (
    <section className="panel">
      <p className="eyebrow">Geospatial Safety Analytics</p>
      <h2>Plant heatmap</h2>
      <div className="mini-zone-grid">
        {["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Utilities"].map((zone) => (
          <div className={`mini-zone ${zone === "Zone C" ? "critical" : ""}`} key={zone}>
            <strong>{zone}</strong>
            <p>{zone === "Zone C" ? "Compound hazard" : "Normal"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
