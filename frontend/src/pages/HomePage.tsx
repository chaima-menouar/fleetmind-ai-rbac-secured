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
    description: "Follow vehicle availability and service status without changing operational data.",
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
      .then(([summary, insights]) => {
        setFleet(summary);
        setIntelligence(insights);
      })
      .catch(() => undefined);
  }, []);

  const criticalCount = intelligence?.risk_ranking.filter((item) => item.risk_score >= 60).length ?? 0;
  const topRisk = intelligence?.risk_ranking[0];

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
        <div className="hero-status"><i /> Fleet intelligence ready <span>{fleet?.total_vehicles ?? 5} vehicles visible</span></div>
      </section>

      <section className="overview-strip scroll-reveal" aria-label="Fleet summary">
        <article><span>Active vehicles</span><strong>{fleet ? `${fleet.active_vehicles}/${fleet.total_vehicles}` : "—"}</strong><small>Backend-derived availability</small></article>
        <article><span>Service due</span><strong>{fleet?.maintenance_due ?? "—"}</strong><small>Within the next 7 days</small></article>
        <article><span>Average vehicle health</span><strong>{fleet ? `${fleet.average_health}%` : "—"}</strong><small>Across the visible fleet</small></article>
        <article><span>Critical operational risk</span><strong>{criticalCount}</strong><small>{topRisk ? `${topRisk.vehicle_id} ranked first` : "No ranked signal"}</small></article>
      </section>

      <section className="product-grid scroll-reveal">
        <Link to="/fleet" className="product-tile tile-light scroll-reveal" style={{ "--reveal-delay": "0ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="fleet" /></span>
          <small>VEHICLE CONTROL</small>
          <h2>Every vehicle.<br />One clear view.</h2>
          <p>See health, battery, location and service priority without digging through dashboards.</p>
          <span className="tile-link">Open vehicles <b>→</b></span>
        </Link>

        {canOperate ? (
          <Link to="/predictive-maintenance" className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "130ms" } as React.CSSProperties}>
            <span className="tile-icon"><Icon name="pulse" /></span>
            <small>PREDICTIVE CARE</small>
            <h2>Know sooner.<br />Act smarter.</h2>
            <p>A trained model turns held-out APS sensor records into traceable maintenance-risk evidence.</p>
            <span className="tile-link">View AI maintenance <b>→</b></span>
          </Link>
        ) : (
          <article className="product-tile tile-dark scroll-reveal" style={{ "--reveal-delay": "130ms" } as React.CSSProperties}>
            <span className="tile-icon"><Icon name="shield" /></span>
            <small>VIEWER ACCESS</small>
            <h2>Protected by<br />least privilege.</h2>
            <p>Your account can inspect approved fleet information but cannot run, create, edit, or delete operational actions.</p>
            <span className="tile-link">Read-only session</span>
          </article>
        )}

        <Link to="/assistant" className="product-tile tile-accent scroll-reveal" style={{ "--reveal-delay": "260ms" } as React.CSSProperties}>
          <span className="tile-icon"><Icon name="sparkles" /></span>
          <small>{role === "viewer" ? "VIEWER ASSISTANT" : "FLEET ASSISTANT"}</small>
          <h2>Ask naturally.<br />Understand faster.</h2>
          <p>{role === "viewer" ? "Get grounded explanations of the fleet information visible to your role." : "Move from a question to verified fleet context and a role-appropriate next action."}</p>
          <span className="tile-link">Start a conversation <b>→</b></span>
        </Link>
      </section>
    </div>
  );
}
