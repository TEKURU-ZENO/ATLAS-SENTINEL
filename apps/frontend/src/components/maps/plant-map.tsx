export function PlantMap() {
  return (
    <section className="panel">
      <p className="eyebrow">Geospatial Safety Analytics</p>
      <h2>Plant heatmap</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginTop: 14 }}>
        {["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Utilities"].map((zone) => (
          <div key={zone} style={{ border: "1px solid #d8ded8", borderRadius: 8, padding: 16, background: zone === "Zone C" ? "#fee2e2" : "#dcfce7" }}>
            <strong>{zone}</strong>
            <p>{zone === "Zone C" ? "Compound hazard" : "Normal"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
