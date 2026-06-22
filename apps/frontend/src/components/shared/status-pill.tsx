export function StatusPill({ status }: { status: string }) {
  return <span style={{ borderRadius: 999, background: "#fee2e2", padding: "6px 10px", fontWeight: 800 }}>{status}</span>;
}
