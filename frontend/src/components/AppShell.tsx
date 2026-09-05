import { useEffect } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth, type UserRole } from "../hooks/AuthContext";
import Icon, { type IconName } from "./Icon";

const navigation: { to: string; label: string; icon: IconName; end?: boolean; roles: UserRole[] }[] = [
  { to: "/", label: "Overview", icon: "chart", end: true, roles: ["admin", "technician", "viewer"] },
  { to: "/fleet", label: "Vehicles", icon: "fleet", roles: ["admin", "technician", "viewer"] },
  { to: "/predictive-maintenance", label: "AI maintenance", icon: "pulse", roles: ["admin", "technician"] },
  { to: "/assistant", label: "My assistant", icon: "sparkles", roles: ["admin", "technician", "viewer"] },
  { to: "/marketplace", label: "Assistants", icon: "store", roles: ["admin", "technician"] },
  { to: "/bots/new", label: "Build assistant", icon: "bot", roles: ["admin"] },
  { to: "/admin", label: "Governance", icon: "shield", roles: ["admin"] },
];

const roleLabels: Record<UserRole, string> = {
  admin: "Fleet manager",
  technician: "Technician",
  viewer: "Read-only viewer",
};

export default function AppShell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const initials = (user?.display_name ?? "Fleet Operations")
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  useEffect(() => {
    const reveal = new IntersectionObserver(
      (entries) => entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("is-visible");
      }),
      { threshold: 0.14 },
    );
    const targets = document.querySelectorAll(".scroll-reveal");
    targets.forEach((target) => reveal.observe(target));
    const updateScroll = () => document.documentElement.style.setProperty("--page-scroll", `${window.scrollY}px`);
    window.addEventListener("scroll", updateScroll, { passive: true });
    updateScroll();
    return () => { reveal.disconnect(); window.removeEventListener("scroll", updateScroll); };
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark brand-logo" aria-hidden="true">
            <svg viewBox="0 0 48 48">
              <path className="logo-track" d="M8 31 17 14l7 13 7-13 9 17" />
              <path className="logo-signal" d="M8 31h10l3-6 5 11 4-8h10" />
            </svg>
          </span>
          <span>
            <strong>FleetMind</strong>
            <small>Mobility intelligence</small>
          </span>
        </div>

        <nav className="navigation" aria-label="Main navigation">
          <p className="nav-label">CONTROL CENTER</p>
          {navigation.filter((item) => user && item.roles.includes(user.role)).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            >
              <span className="nav-icon"><Icon name={item.icon} /></span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-status model-status-card">
          <span className="status-symbol"><Icon name="shield" /></span>
          <div>
            <small>AI STATUS</small>
            <strong>Grounded intelligence online</strong>
            <span><i className="status-dot" /> Role scoped · Verified</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-context">
            <span className="topbar-context-icon"><Icon name="pulse" /></span>
            <div><strong>FleetMind One</strong><small>Intelligent mobility platform</small></div>
          </div>
          <div className="topbar-actions">
            <span className="environment-pill"><i /> Grounded AI active</span>
            <div className="user-chip">
              <span className="avatar">{initials}</span>
              <span>
                <strong>{user?.display_name ?? "Fleet Operations"}</strong>
                <small>{user ? roleLabels[user.role] : "Fleet user"}</small>
              </span>
            </div>
            <button className="logout-button" type="button" onClick={() => { logout(); navigate("/login", { replace: true }); }}>Sign out</button>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
