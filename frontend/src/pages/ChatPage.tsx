import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listBots } from "../api/bots";
import type { Bot } from "../api/types";
import ChatWindow from "../components/ChatWindow";
import { useAuth } from "../hooks/AuthContext";

const roleCopy = {
  admin: {
    eyebrow: "MANAGER INTELLIGENCE",
    title: "Lead the fleet with verified context.",
    description: "Your assistant receives deterministic fleet KPIs and risk rankings before it explains priorities, availability, cost, or operational risk.",
    boundary: "Management guidance only — no step-by-step repair procedures.",
  },
  technician: {
    eyebrow: "TECHNICIAN INTELLIGENCE",
    title: "Diagnose faster. Stay evidence-led.",
    description: "Your assistant combines verified fleet facts with approved technical knowledge for maintenance, fault triage, service procedures, and safety checks.",
    boundary: "Technical support only — no fleet-management or commercial decisions.",
  },
  viewer: {
    eyebrow: "VIEWER INTELLIGENCE",
    title: "Understand the fleet without changing it.",
    description: "Your read-only assistant explains approved fleet status, risk indicators, metrics, and service dates while operational actions remain blocked.",
    boundary: "Read-only explanations — no tasks, writes, or restricted internal actions.",
  },
} as const;

export default function ChatPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [bots, setBots] = useState<Bot[]>([]);
  const [error, setError] = useState<string>();

  useEffect(() => {
    listBots()
      .then(setBots)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load your assistant."));
  }, []);

  const copy = user ? roleCopy[user.role] : roleCopy.viewer;

  return (
    <div className="page chat-page">
      <div className="page-heading compact">
        <div>
          <span className="eyebrow">{copy.eyebrow}</span>
          <h1>{copy.title}</h1>
          <p>{copy.description}</p>
          <div className="hero-pills">
            <span><i className="pill-dot cyan" /> Deterministic fleet facts</span>
            <span><i className="pill-dot violet" /> Retrieved approved knowledge</span>
            <span><i className="pill-dot pink" /> Server-enforced role scope</span>
          </div>
        </div>
        <span className="demo-badge">GROUNDED AI</span>
      </div>
      <section className="data-boundary-banner">
        <div>
          <strong>{copy.boundary}</strong>
          <span>Fleet telemetry and service facts are computed or retrieved before generation; the assistant is instructed not to invent them.</span>
        </div>
      </section>
      {error && <div className="inline-error">{error}</div>}
      {bots.length > 0 ? (
        <ChatWindow bots={bots} initialBotId={searchParams.get("bot") ?? undefined} />
      ) : !error ? (
        <div className="loading-card">Loading your FleetMind assistant…</div>
      ) : null}
    </div>
  );
}
