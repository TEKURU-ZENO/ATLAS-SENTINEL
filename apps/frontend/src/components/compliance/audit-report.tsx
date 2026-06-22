export function AuditReport() {
  return <main className="page"><p className="eyebrow">Autonomous Compliance Monitoring</p><h1>Audit package</h1><ViolationCard /><RegulationViewer /></main>;
}

import { RegulationViewer } from "./regulation-viewer";
import { ViolationCard } from "./violation-card";
