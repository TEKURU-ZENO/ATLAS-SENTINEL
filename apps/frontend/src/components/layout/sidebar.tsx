const links = [
  ["Command", "/command-center"],
  ["Digital Twin", "/digital-twin"],
  ["Incidents", "/incidents"],
  ["Permits", "/permits"],
  ["Compliance", "/compliance"],
  ["Analytics", "/analytics"],
  ["Copilot", "/copilot"],
  ["Settings", "/settings"]
];

export function Sidebar() {
  return (
    <aside style={{ background: "#202923", color: "#eef5ed", padding: 20, minHeight: "100vh" }}>
      <strong>ATLAS Sentinel</strong>
      <nav style={{ display: "grid", gap: 10, marginTop: 24 }}>
        {links.map(([label, href]) => (
          <a key={href} href={href}>{label}</a>
        ))}
      </nav>
    </aside>
  );
}
