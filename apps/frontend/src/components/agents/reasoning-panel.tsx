const reasoning = [
  "Gas concentration rising in Zone C.",
  "Hot work permit PTW-4421 is active for Boiler 7.",
  "Shift handover is in progress, increasing coordination risk.",
  "Similar conditions preceded 3 historical incidents."
];

export function ReasoningPanel() {
  return (
    <section className="panel">
      <p className="eyebrow">Agentic Safety Orchestration</p>
      <h2>Agent reasoning</h2>
      <ol>
        {reasoning.map((item) => <li key={item}>{item}</li>)}
      </ol>
    </section>
  );
}
