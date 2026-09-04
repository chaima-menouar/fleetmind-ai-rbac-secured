import { Link } from "react-router-dom";
import Icon from "../components/Icon";
import { useAuth, type UserRole } from "../hooks/AuthContext";

const roleCopy: Record<UserRole, { kicker: string; title: string; description: string }> = {
  admin: {
    kicker: "MANAGER CONTROL CENTER",
    title: "Lead every fleet decision.",
    description: "Manage fleet health, AI operations, assistants, and governance from one protected workspace.",
  },
  technician: {
    kicker: "TECHNICIAN WORKSPACE",
    title: "Diagnose sooner. Service smarter.",
    description: "Prioritize vehicle risk, run maintenance triage, and use approved technical knowledge.",
  },
  viewer: {
    kicker: "READ-ONLY FLEET VIEW",
    title: "Fleet status. Clearly visible.",
    description: "Follow vehicle availability and service status without changing operational data.",
  },
};

export default function HomePage() {
  const { user } = useAuth();
  const role = user?.role ?? "viewer";
  const copy = roleCopy[role];
  const canOperate = role !== "viewer";

  return (
    <div className="home-page">
      <section className="product-hero hero-enter">
       <img src="/fleetmind-dashboard.png" alt="FleetMind vehicle dashboard" /> 
        <div className="hero-shade" />
        <div className="product-hero-copy">
          <span className="hero-kicker">{copy.kicker}</span>
          <h1>{copy.title}</h1>
          <p>{copy.description}</p>
          <div className="hero-actions">
            <Link className="hero-button hero-button-light" to="/fleet">Explore your fleet</Link>
            {canOperate && <Link className="hero-button hero-button-glass" to="/assistant">Ask FleetMind</Link>}
            {role === "admin" && <Link className="hero-button hero-button-glass" to="/admin">Open governance</Link>}
          </div>
        </div>
        <div className="hero-status"><i /> Fleet connected <span>5 vehicles online</span></div>
      </section>

      <section className="overview-strip scroll-reveal" aria-label="Fleet summary">
        <article><span>Fleet availability</span><strong>96%</strong><small>4 vehicles ready</small></article>
        <article><span>Maintenance attention</span><strong>2</strong><small>Prioritized by AI</small></article>
        <article><span>Average vehicle health</span><strong>84%</strong><small>Across the fleet</small></article>
        <article><span>Model readiness</span><strong>93.1%</strong><small>APS failure recall</small></article>
      </section>

      <section className="product-grid scroll-reveal">
        <Link to="/fleet" className="product-tile tile-light scroll-reveal" style={{ "--reveal-delay": "0ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="fleet" /></span>
          <small>VEHICLE CONTROL</small>
          <h2>Every vehicle.<br />One clear view.</h2>
          <p>See health, battery, location and service priority without digging through dashboards.</p>
          <span className="tile-link">Open vehicles <b>→</b></span>
        </Link>
        {canOperate && <Link to="/predictive-maintenance" className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "130ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="pulse" /></span>
          <small>PREDICTIVE CARE</small>
          <h2>Know sooner.<br />Act smarter.</h2>
          <p>A trained machine-learning model turns sensor data into an early, actionable warning.</p>
          <span className="tile-link">View AI maintenance <b>→</b></span>
        </Link>}
        {canOperate && <Link to="/assistant" className="product-tile tile-accent scroll-reveal" style={{ "--reveal-delay": "260ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="sparkles" /></span>
          <small>FLEET ASSISTANT</small>
          <h2>Ask naturally.<br />Decide confidently.</h2>
          <p>Move from a question to the right vehicle, explanation and next action in seconds.</p>
          <span className="tile-link">Start a conversation <b>→</b></span>
        </Link>}
        {role === "viewer" && <article className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "130ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="shield" /></span>
          <small>VIEWER ACCESS</small>
          <h2>Protected by<br />least privilege.</h2>
          <p>Your account can inspect approved fleet information but cannot run, create, edit, or delete operational actions.</p>
          <span className="tile-link">Read-only session</span>
        </article>}
      </section>
    </div>
  );
}
