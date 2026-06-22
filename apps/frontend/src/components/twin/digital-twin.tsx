export function DigitalTwin() {
  return (
    <main className="page">
      <p className="eyebrow">Industrial Digital Twin</p>
      <h1>Live plant state</h1>
      <div className="grid">
        <EquipmentCard />
        <WorkerCard />
        <TwinTimeline />
      </div>
    </main>
  );
}

import { EquipmentCard } from "./equipment-card";
import { WorkerCard } from "./worker-card";
import { TwinTimeline } from "./twin-timeline";
