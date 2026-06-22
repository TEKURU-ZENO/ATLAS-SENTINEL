import { KpiStrip } from "../components/command/kpi-strip";
import { PlantMap } from "../components/maps/plant-map";
import { ReasoningPanel } from "../components/agents/reasoning-panel";
import { ActionCenter } from "../components/command/action-center";

export default function HomePage() {
  return (
    <main className="page">
      <section>
        <p className="eyebrow">Industrial Safety Intelligence Operating System</p>
        <h1>Command center</h1>
      </section>
      <KpiStrip />
      <div className="grid">
        <PlantMap />
        <ReasoningPanel />
        <ActionCenter />
      </div>
    </main>
  );
}
