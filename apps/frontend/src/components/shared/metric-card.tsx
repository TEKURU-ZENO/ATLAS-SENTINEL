export function MetricCard({ label, value }: { label: string; value: string }) {
  return <div className="panel"><p className="eyebrow">{label}</p><strong>{value}</strong></div>;
}
