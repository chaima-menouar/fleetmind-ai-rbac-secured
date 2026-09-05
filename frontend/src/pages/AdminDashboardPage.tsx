import { useEffect, useState } from "react";
import {
  getReadinessStatus,
  getUsageStats,
  type ReadinessStatus,
} from "../api/admin";
import type { UsageStats } from "../api/types";
import StatCard from "../components/StatCard";
import Icon from "../components/Icon";

export default function AdminDashboardPage() {
  const [usage, setUsage] = useState<UsageStats>();
  const [readiness, setReadiness] = useState<ReadinessStatus>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    Promise.all([getUsageStats(), getReadinessStatus()])
      .then(([usageStats, runtime]) => {
        setUsage(usageStats);
        setReadiness(runtime);
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load governance data."));
  }, []);

  const maximum = Math.max(1, ...Object.values(usage?.messages_by_bot ?? {}));

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">ADMIN & GOVERNANCE</span>
          <h1>Responsible AI, <span>visible by design.</span></h1>
          <p>Track assistant usage, model readiness, grounding, and runtime boundaries.</p>
        </div>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {usage && readiness ? (
        <>
          <div className="stat-grid">
            <StatCard label="AI responses" value={usage.total_messages} detail="This application session" />
            <StatCard label="Agent runs" value={usage.total_agent_runs} detail="Auditable automations" tone="violet" />
            <StatCard label="Conversations" value={usage.active_conversations} detail="Active demo threads" tone="green" />
            <StatCard
              label="Predictive model"
              value={readiness.predictive_model_status === "ready" ? "Ready" : "Unavailable"}
              detail={readiness.predictive_model_version}
              tone={readiness.predictive_model_status === "ready" ? "green" : "amber"}
            />
          </div>

          <section className="data-boundary-banner">
            <div>
              <strong>AI runtime evidence</strong>
              <span>
                {readiness.grounding}. Provider: {readiness.llm_provider}. Storage: {readiness.persistence}.
              </span>
            </div>
            <span className="section-count">{readiness.environment}</span>
          </section>

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
              <div className="section-heading"><div><h2>Governance controls</h2><p>Runtime and deployment boundary</p></div></div>
              <ul className="check-list">
                <li><span><Icon name="check" /></span><div><strong>Grounded fleet facts</strong><small>Deterministic analytics before generative explanation</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Server-enforced roles</strong><small>Manager, technician, and viewer permissions at API boundary</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Predictive artifact integrity</strong><small>Bundled model hash verified before inference</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Restricted CORS</strong><small>{readiness.cors_origins} configured origin{readiness.cors_origins === 1 ? "" : "s"}</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Authentication boundary</strong><small>{readiness.authentication}</small></div></li>
                <li><span><Icon name="check" /></span><div><strong>Demo isolation</strong><small>{readiness.demo_mode ? "Fictional fleet records only" : "Production mode"}</small></div></li>
              </ul>
            </section>
          </div>
        </>
      ) : !error ? <div className="loading-card">Loading governance evidence…</div> : null}
    </div>
  );
}
