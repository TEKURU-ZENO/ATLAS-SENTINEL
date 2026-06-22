export function ChatWindow() {
  return (
    <main className="page">
      <p className="eyebrow">Safety Copilot</p>
      <h1>Field answer</h1>
      <div className="panel">
        <p><strong>Worker:</strong> Can I start welding in Zone C?</p>
        <p><strong>ATLAS:</strong> Unsafe. Methane exceeds safe hot work conditions. Suspend PTW-4421 and evacuate Zone C.</p>
      </div>
      <CitationPanel />
    </main>
  );
}

import { CitationPanel } from "./citation-panel";
