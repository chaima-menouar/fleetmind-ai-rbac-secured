import { apiFetch } from "./client";
import type { UsageStats } from "./types";

export interface ReadinessStatus {
  environment: string;
  demo_mode: boolean;
  llm_provider: string;
  grounding: string;
  predictive_model_status: "ready" | "unavailable";
  predictive_model_version: string;
  persistence: string;
  authentication: string;
  cors_origins: number;
}

export function getUsageStats() {
  return apiFetch<UsageStats>("/api/admin/usage");
}

export function getReadinessStatus() {
  return apiFetch<ReadinessStatus>("/api/admin/readiness");
}
