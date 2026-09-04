import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFleetSummary, runMaintenanceTriage } from "../api/fleet";
import type { AgentTask, FleetSummary } from "../api/types";
import StatCard from "../components/StatCard";
import Icon from "../components/Icon";
import { useAuth } from "../hooks/AuthContext";

export default function FleetDashboardPage() {
  const { user } = useAuth();
  const canRunTriage = user?.role !== "viewer";
  const [fleet, setFleet] = useState<FleetSummary>();
  const [task, setTask] = useState<AgentTask>();
  const [runningVehicle, setRunningVehicle] = useState<string>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    getFleetSummary()
      .then(setFleet)
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
          <p>Demo telemetry from five vehicles with one-click maintenance triage.</p>
        </div>
        <span className="last-updated">● Demo data · updated now</span>
      </div>
      {error && <div className="inline-error">{error}</div>}
      {fleet && (
        <>
          <section className="data-boundary-banner">
            <div>
              <strong>This page uses fictional fleet data and deterministic triage rules.</strong>
              <span>The separately evaluated Scania APS classifier is available in Predictive ML.</span>
            </div>
            <Link to="/predictive-maintenance">View real model evidence →</Link>
          </section>
          <div className="stat-grid">
            <StatCard label="Total vehicles" value={fleet.total_vehicles} detail="Across 5 Moroccan cities" />
            <StatCard label="Active now" value={fleet.active_vehicles} detail="Ready for operations" tone="green" />
            <StatCard label="Service due" value={fleet.maintenance_due} detail="Within the next 7 days" tone="amber" />
            <StatCard label="Average health" value={`${fleet.average_health}%`} detail="Fleet-wide health score" tone="violet" />
          </div>

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
        </>
      )}
    </div>
  );
}
