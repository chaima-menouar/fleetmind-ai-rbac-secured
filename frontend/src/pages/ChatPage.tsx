import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listBots } from "../api/bots";
import type { Bot } from "../api/types";
import ChatWindow from "../components/ChatWindow";
import { useAuth } from "../hooks/AuthContext";

export default function ChatPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [bots, setBots] = useState<Bot[]>([]);
  const [error, setError] = useState<string>();

  useEffect(() => {
    listBots()
      .then(setBots)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load bots."));
  }, []);

  return (
    <div className="page chat-page">
      <div className="page-heading compact">
        <div>
          <span className="eyebrow">AI WORKSPACE</span>
          <h1>Operational intelligence, <span>one question away.</span></h1>
          <p>Turn fleet data and approved knowledge into clear next actions.</p>
          <div className="hero-pills">
            <span><i className="pill-dot cyan" /> {bots.length || 3} specialist assistants</span>
            <span><i className="pill-dot violet" /> Grounded answers</span>
            <span><i className="pill-dot pink" /> Safety-aware</span>
          </div>
        </div>
        <span className="demo-badge">DEMO MODE</span>
      </div>
      {error && <div className="inline-error">{error} Is the backend running on port 8000?</div>}
      {bots.length > 0 ? (
        <ChatWindow bots={bots} initialBotId={searchParams.get("bot") ?? undefined} readOnly={user?.role === "viewer"} />
      ) : !error ? (
        <div className="loading-card">Loading FleetMind assistants…</div>
      ) : null}
    </div>
  );
}
