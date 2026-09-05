import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listBots } from "../api/bots";
import type { Bot } from "../api/types";
import ChatWindow from "../components/ChatWindow";
import { useAuth } from "../hooks/AuthContext";

const roleCopy = {
  admin: {
    eyebrow: "MANAGER INTELLIGENCE",
    title: "Lead the fleet with the right context.",
    description: "Your assistant focuses on fleet KPIs, risk, availability, priorities, and management decisions.",
  },
  technician: {
    eyebrow: "TECHNICIAN INTELLIGENCE",
    title: "Diagnose faster. Service with confidence.",
    description: "Your assistant focuses on maintenance, alerts, service procedures, fault triage, and safety checks.",
  },
  viewer: {
    eyebrow: "VIEWER INTELLIGENCE",
    title: "Understand what you can see.",
    description: "Your read-only assistant explains fleet status and dashboard information without performing restricted actions.",
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
            <span><i className="pill-dot cyan" /> Role-scoped assistant</span>
            <span><i className="pill-dot violet" /> Grounded answers</span>
            <span><i className="pill-dot pink" /> Server-enforced access</span>
          </div>
        </div>
        <span className="demo-badge">ROLE AWARE</span>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {bots.length > 0 ? (
        <ChatWindow bots={bots} initialBotId={searchParams.get("bot") ?? undefined} />
      ) : !error ? (
        <div className="loading-card">Loading your FleetMind assistant…</div>
      ) : null}
    </div>
  );
}
