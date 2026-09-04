import { apiFetch } from "./client";
import type { ChatResponse } from "./types";

export function sendMessage(content: string, botId: string, conversationId?: string) {
  return apiFetch<ChatResponse>("/api/chat/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, bot_id: botId, conversation_id: conversationId }),
  });
}
