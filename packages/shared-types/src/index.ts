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

export interface RiskForecast {
  current: number;
  forecast30: number;
  forecast60: number;
  tone: RiskTone;
}
