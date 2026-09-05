import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFleetIntelligence, getFleetSummary } from "../api/fleet";
import type { FleetIntelligence, FleetSummary } from "../api/types";
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
    description: "Follow approved fleet intelligence and ask a read-only assistant without changing operational data.",
  },
};

export default function HomePage() {
  const { user } = useAuth();
  const role = user?.role ?? "viewer";
  const copy = roleCopy[role];
  const canOperate = role !== "viewer";
  const [fleet, setFleet] = useState<FleetSummary>();
  const [intelligence, setIntelligence] = useState<FleetIntelligence>();

  useEffect(() => {
    Promise.all([getFleetSummary(), getFleetIntelligence()])
      .then(([summary, grounded]) => {
        setFleet(summary);
        setIntelligence(grounded);
      })
      .catch(() => undefined);
  }, []);

  const availability = fleet ? Math.round((fleet.active_vehicles / fleet.total_vehicles) * 100) : undefined;
  const criticalCount = intelligence?.critical_vehicle_ids.length;

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
            <Link className="hero-button hero-button-glass" to="/assistant">Ask FleetMind</Link>
            {role === "admin" && <Link className="hero-button hero-button-glass" to="/admin">Open governance</Link>}
          </div>
        </div>
        <div className="hero-status"><i /> Fleet connected <span>{fleet ? `${fleet.total_vehicles} vehicles visible` : "Secure session"}</span></div>
      </section>

      <section className="overview-strip scroll-reveal" aria-label="Fleet summary">
        <article><span>Fleet availability</span><strong>{availability === undefined ? "—" : `${availability}%`}</strong><small>Derived from current status</small></article>
        <article><span>Service due ≤7 days</span><strong>{fleet?.maintenance_due ?? "—"}</strong><small>Deterministic fleet KPI</small></article>
        <article><span>Average vehicle health</span><strong>{fleet ? `${fleet.average_health}%` : "—"}</strong><small>Across visible vehicles</small></article>
        <article><span>Critical operational risk</span><strong>{criticalCount ?? "—"}</strong><small>Composite rule-based score</small></article>
      </section>

      <section className="product-grid scroll-reveal">
        <Link to="/fleet" className="product-tile tile-light scroll-reveal" style={{ "--reveal-delay": "0ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="fleet" /></span>
          <small>GROUNDED FLEET CONTROL</small>
          <h2>Every vehicle.<br />One verified view.</h2>
          <p>See health, battery, service urgency and deterministic risk before any AI explanation is generated.</p>
          <span className="tile-link">Open vehicles <b>→</b></span>
        </Link>
        {canOperate && <Link to="/predictive-maintenance" className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "130ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="pulse" /></span>
          <small>PREDICTIVE ML</small>
          <h2>Measured model.<br />Visible evidence.</h2>
          <p>The Scania APS classifier exposes its dataset, threshold, metrics and limitations instead of hiding model quality.</p>
          <span className="tile-link">View model evidence <b>→</b></span>
        </Link>}
        <Link to="/assistant" className="product-tile tile-accent scroll-reveal" style={{ "--reveal-delay": "260ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="sparkles" /></span>
          <small>{role === "viewer" ? "READ-ONLY ASSISTANT" : "ROLE-SCOPED ASSISTANT"}</small>
          <h2>Ask naturally.<br />Stay grounded.</h2>
          <p>{role === "viewer" ? "Explain approved fleet status without running operational actions." : "Verified fleet analytics and approved knowledge are injected before the LLM responds."}</p>
          <span className="tile-link">Start a conversation <b>→</b></span>
        </Link>
        {role === "viewer" && <article className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "390ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="shield" /></span>
          <small>LEAST PRIVILEGE</small>
          <h2>Useful access.<br />No operational writes.</h2>
          <p>Your role can inspect approved fleet information and use its viewer assistant while restricted actions remain blocked by the backend.</p>
          <span className="tile-link">Server-enforced access</span>
        </article>}
      </section>
    </div>
  );
}
