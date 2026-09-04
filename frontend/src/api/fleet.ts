import { apiFetch } from "./client";
import type { AgentTask, FleetSummary } from "./types";

export function getFleetSummary() {
  return apiFetch<FleetSummary>("/api/fleet/summary");
}

export function runMaintenanceTriage(vehicleId: string) {
  return apiFetch<AgentTask>("/api/agents/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_type: "maintenance_triage", vehicle_id: vehicleId }),
  });
}
