export function ActionCenter() {
  return (
    <section className="panel">
      <p className="eyebrow">Emergency Commander Agent</p>
      <h2>Recommended action</h2>
      <p>Evacuate Zone C, suspend hot work permit PTW-4421, alert emergency response, and preserve evidence.</p>
      <button style={{ border: 0, borderRadius: 8, background: "#c92323", color: "#fff", padding: "12px 14px", fontWeight: 800 }}>
        Trigger workflow
      </button>
    </section>
  );
}
