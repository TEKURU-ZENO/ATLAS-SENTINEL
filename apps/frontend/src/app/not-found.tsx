export default function NotFound() {
  return (
    <main className="page">
      <section className="command-panel">
        <p className="eyebrow">ATLAS Sentinel</p>
        <h1>Command surface unavailable</h1>
        <p>The requested view is not configured in this deployment.</p>
        <a className="button primary-button" href="/">Return to command center</a>
      </section>
    </main>
  );
}
