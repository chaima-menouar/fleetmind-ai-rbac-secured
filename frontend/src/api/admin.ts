import { apiFetch } from "./client";
import type { UsageStats } from "./types";

export function getUsageStats() {
  return apiFetch<UsageStats>("/api/admin/usage");
}
