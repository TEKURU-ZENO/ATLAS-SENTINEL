export function Chart({ values }: { values: number[] }) {
  return (
    <div className="panel chart-panel">
      {values.map((value, index) => (
        <div
          className={`chart-bar ${value > 80 ? "critical" : ""}`}
          key={`${value}-${index}`}
          style={{ height: value * 2 }}
        />
      ))}
    </div>
  );
}
