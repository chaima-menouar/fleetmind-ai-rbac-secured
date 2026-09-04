import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listBots } from "../api/bots";
import type { Bot } from "../api/types";
import BotCard from "../components/BotCard";
import { useAuth } from "../hooks/AuthContext";

export default function MarketplacePage() {
  const { user } = useAuth();
  const [bots, setBots] = useState<Bot[]>([]);
  const [error, setError] = useState<string>();

  useEffect(() => {
    listBots(true)
      .then(setBots)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load bots."));
  }, []);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">AI MARKETPLACE</span>
          <h1>Expert assistants for <span>every team.</span></h1>
          <p>Discover approved copilots built around your departments and trusted knowledge.</p>
        </div>
        {user?.role === "admin" && <Link className="primary-button" to="/bots/new">+ Build an assistant</Link>}
      </div>
      {error && <div className="inline-error">{error}</div>}
      <div className="marketplace-meta">
        <span><i /> {bots.length} approved assistants</span>
        <span>Curated for enterprise workflows</span>
      </div>
      <div className="bot-grid">
        {bots.map((bot) => <BotCard key={bot.id} bot={bot} />)}
      </div>
    </div>
  );
}
