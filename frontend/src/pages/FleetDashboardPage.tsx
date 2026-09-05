import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFleetIntelligence, getFleetSummary, runMaintenanceTriage } from "../api/fleet";
import type { AgentTask, FleetIntelligence, FleetSummary } from "../api/types";
import StatCard from "../components/StatCard";
import Icon from "../components/Icon";
import { useAuth } from "../hooks/AuthContext";

export default function FleetDashboardPage() {
  const { user } = useAuth();
  const canRunTriage = user?.role !== "viewer";
  const [fleet, setFleet] = useState<FleetSummary>();
  const [intelligence, setIntelligence] = useState<FleetIntelligence>();
  const [task, setTask] = useState<AgentTask>();
  const [runningVehicle, setRunningVehicle] = useState<string>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    Promise.all([getFleetSummary(), getFleetIntelligence()])
      .then(([summary, grounded]) => {
        setFleet(summary);
        setIntelligence(grounded);
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load fleet."));
  }, []);

  const runTriage = async (vehicleId: string) => {
    setRunningVehicle(vehicleId);
    setError(undefined);
    try {
      setTask(await runMaintenanceTriage(vehicleId));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The agent could not run.");
    } finally {
      setRunningVehicle(undefined);
    }
  };

  if (!fleet && !error) return <div className="loading-card">Loading live fleet overview…</div>;

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">FLEET COMMAND</span>
          <h1>See risk before it <span>becomes downtime.</span></h1>
          <p>Verified analytics first, AI explanation second — with role-aware operational controls.</p>
        </div>
        <span className="last-updated">● Grounded demo telemetry · updated now</span>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {fleet && (
        <>
          <section className="data-boundary-banner">
            <div>
              <strong>Fleet facts are computed before they reach the assistant.</strong>
              <span>Risk scores and KPIs below come from deterministic analytics, not LLM guesses.</span>
            </div>
            <Link to="/assistant">Ask my assistant →</Link>
          </section>

          <div className="stat-grid">
            <StatCard label="Total vehicles" value={fleet.total_vehicles} detail="Across 5 Moroccan cities" />
            <StatCard label="Active now" value={fleet.active_vehicles} detail="Ready for operations" tone="green" />
            <StatCard label="Service due" value={fleet.maintenance_due} detail="Within the next 7 days" tone="amber" />
            <StatCard label="Average health" value={`${fleet.average_health}%`} detail="Fleet-wide health score" tone="violet" />
          </div>

          {intelligence && (
            <section className="table-card">
              <div className="section-heading">
                <div>
                  <h2>Grounded intelligence</h2>
                  <p>Deterministic signals used to constrain manager, technician, and viewer assistants.</p>
                </div>
                <span className="demo-badge">NO LLM CALCULATION</span>
              </div>
              <div className="stat-grid">
                {intelligence.kpis.slice(0, 4).map((kpi, index) => (
                  <StatCard
                    key={kpi.label}
                    label={kpi.label}
                    value={kpi.value}
                    detail={kpi.detail}
                    tone={index === 0 ? "green" : index === 3 ? "amber" : "violet"}
                  />
                ))}
              </div>
              <div className="section-heading">
                <div>
                  <h2>Operational risk ranking</h2>
                  <p>Composite score from status, health, battery, and service urgency.</p>
                </div>
                <span className="section-count">{intelligence.critical_vehicle_ids.length} critical</span>
              </div>
              <div className="table-scroll">
                <table>
                  <thead><tr><th>Rank</th><th>Vehicle</th><th>Risk</th><th>Health</th><th>Battery</th><th>Service</th><th>Location</th></tr></thead>
                  <tbody>
                    {intelligence.risk_ranking.slice(0, 5).map((risk, index) => (
                      <tr key={risk.vehicle_id}>
                        <td><strong>#{index + 1}</strong></td>
                        <td><strong>{risk.vehicle_id}</strong><small>{risk.model}</small></td>
                        <td><strong>{risk.risk_score}</strong><small>{risk.risk_score >= 60 ? "Critical" : risk.risk_score >= 30 ? "Watch" : "Stable"}</small></td>
                        <td>{risk.health_score}%</td>
                        <td>{risk.battery_percent}%</td>
                        <td>{risk.next_service_days === 0 ? "Due now" : `${risk.next_service_days} days`}</td>
                        <td>{risk.location}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {task && (
            <section className="agent-result">
              <span className="agent-result-icon"><Icon name="sparkles" /></span>
              <div>
                <span className="eyebrow">AGENT RUN COMPLETE</span>
                <h3>{task.summary}</h3>
                <p>Task {task.task_id}{task.output.ticket ? ` · Ticket ${task.output.ticket.ticket_id}` : " · No ticket required"}</p>
              </div>
              <button type="button" onClick={() => setTask(undefined)} aria-label="Dismiss">×</button>
            </section>
          )}

          <section className="table-card">
            <div className="section-heading">
              <div><h2>Vehicle health</h2><p>Prioritized by maintenance urgency</p></div>
              <span className="section-count">{fleet.vehicles.length} vehicles</span>
            </div>
            <div className="table-scroll">
              <table>
                <thead><tr><th>Vehicle</th><th>Driver & location</th><th>Battery</th><th>Health</th><th>Status</th><th>Next service</th><th /></tr></thead>
                <tbody>
                  {[...fleet.vehicles].sort((a, b) => a.health_score - b.health_score).map((vehicle) => (
                    <tr key={vehicle.id}>
                      <td><strong>{vehicle.id}</strong><small>{vehicle.model}</small></td>
                      <td><strong>{vehicle.driver}</strong><small>{vehicle.location}</small></td>
                      <td><div className="meter"><span style={{ width: `${vehicle.battery_percent}%` }} /></div><small>{vehicle.battery_percent}%</small></td>
                      <td><strong>{vehicle.health_score}%</strong></td>
                      <td><span className={`status-badge status-${vehicle.status}`}>{vehicle.status}</span></td>
                      <td>{vehicle.next_service_days === 0 ? "Due now" : `${vehicle.next_service_days} days`}</td>
                      <td><button className="table-action" type="button" disabled={!canRunTriage || runningVehicle === vehicle.id} title={!canRunTriage ? "Viewer access is read-only" : undefined} onClick={() => void runTriage(vehicle.id)}>{!canRunTriage ? "View only" : runningVehicle === vehicle.id ? "Running…" : "Run triage"}</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="data-boundary-banner">
            <div>
              <strong>Predictive ML remains separately evaluated.</strong>
              <span>The Scania APS classifier is not used to fabricate this fictional fleet telemetry.</span>
            </div>
            <Link to="/predictive-maintenance">View model evidence →</Link>
          </section>
        </>
      )}
    </div>
  );
}
