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
    <aside className="sidebar">
      <a className="brand-lockup" href="/">
        <span className="brand-mark">AS</span>
        <span>
          <strong>ATLAS Sentinel</strong>
          <small>Safety OS</small>
        </span>
      </a>
      <nav className="sidebar-nav" aria-label="Primary navigation">
        {links.map(([label, href]) => (
          <a key={href} href={href}>{label}</a>
        ))}
      </nav>
      <div className="sidebar-status">
        <span className="status-dot" />
        <span>Digital twin online</span>
      </div>
    </aside>
  );
}
