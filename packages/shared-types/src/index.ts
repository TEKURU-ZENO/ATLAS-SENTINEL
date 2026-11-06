export type RiskTone = "green" | "yellow" | "orange" | "red";

export interface TwinState {
  zone: string;
  equipment: string;
  methanePercentLel: number;
  activeHotWork: boolean;
  maintenanceActive: boolean;
  shiftHandover: boolean;
  workers: number;
}

export interface RiskSnapshot {
  current: number | null;
  snapshotScore: number | null;
  sensorTrend: "rising" | "falling" | "stable" | "unknown";
  sensorDelta: number | null;
  tone: RiskTone;
}
