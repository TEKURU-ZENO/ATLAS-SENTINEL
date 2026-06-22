import { Chart } from "../../components/shared/chart";

export default function AnalyticsPage() {
  return (
    <main className="page">
      <p className="eyebrow">Predictive Hazard Forecasting</p>
      <h1>Risk analytics</h1>
      <Chart values={[18, 43, 63, 86, 94]} />
    </main>
  );
}
