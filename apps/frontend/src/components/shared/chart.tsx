export function Chart({ values }: { values: number[] }) {
  return (
    <div className="panel" style={{ display: "flex", alignItems: "end", gap: 10, height: 260 }}>
      {values.map((value, index) => (
        <div key={`${value}-${index}`} style={{ height: value * 2, width: 46, borderRadius: "8px 8px 0 0", background: value > 80 ? "#c92323" : "#087f8c" }} />
      ))}
    </div>
  );
}
