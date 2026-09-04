import { useEffect, useState } from "react";
import { getUsageStats } from "../api/admin";
import type { UsageStats } from "../api/types";
import StatCard from "../components/StatCard";
import Icon from "../components/Icon";

export default function AdminDashboardPage() {
  const [usage, setUsage] = useState<UsageStats>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    getUsageStats()
      .then(setUsage)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load usage."));
  }, []);

  const maximum = Math.max(1, ...Object.values(usage?.messages_by_bot ?? {}));

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">ADMIN & GOVERNANCE</span>
          <h1>Responsible AI, <span>visible by design.</span></h1>
          <p>Track assistant adoption and agent activity across this demo workspace.</p>
        </div>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {usage ? (
        <>
          <div className="stat-grid">
            <StatCard label="AI responses" value={usage.total_messages} detail="This application session" />
            <StatCard label="Agent runs" value={usage.total_agent_runs} detail="Auditable automations" tone="violet" />
            <StatCard label="Conversations" value={usage.active_conversations} detail="Active demo threads" tone="green" />
            <StatCard label="Shared assistants" value={usage.published_bots} detail="Visible in marketplace" tone="amber" />
          </div>
          <div className="admin-grid">
            <section className="panel-card">
              <div className="section-heading"><div><h2>Messages by assistant</h2><p>Live in-memory usage</p></div></div>
              {Object.keys(usage.messages_by_bot).length ? (
                <div className="bar-list">
                  {Object.entries(usage.messages_by_bot).map(([bot, count]) => (
                    <div className="bar-item" key={bot}>
                      <span>{bot}</span><div><i style={{ width: `${(count / maximum) * 100}%` }} /></div><strong>{count}</strong>
                    </div>
                  ))}
                </div>
              ) : <div className="empty-state">Send a chat message to generate the first usage signal.</div>}
            </section>
            <section className="panel-card governance-card">
              <div className="section-heading"><div><h2>Governance controls</h2><p>Deployment readiness</p></div></div>
              <ul className="check-list">
                <li><span><Icon name="check" /></span><div><strong>Restricted CORS</strong><small>Configured per environment</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Cognito boundary</strong><small>JWT authorizer available in CDK</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Safe knowledge uploads</strong><small>Type and size validation</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Demo isolation</strong><small>No real customer or vehicle data</small></div></li>
              </ul>
            </section>
          </div>
        </>
      ) : !error ? <div className="loading-card">Loading usage analytics…</div> : null}
    </div>
  );
}
