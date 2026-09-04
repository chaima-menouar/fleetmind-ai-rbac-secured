import { apiFetch } from "./client";
import type { Bot, Department } from "./types";

export interface CreateBotPayload {
  name: string;
  department: Department;
  description: string;
  system_prompt: string;
  is_shared: boolean;
}

export function listBots(sharedOnly = false) {
  return apiFetch<Bot[]>(`/api/bots?shared_only=${sharedOnly}`);
}

export function createBot(payload: CreateBotPayload) {
  return apiFetch<Bot>("/api/bots", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
