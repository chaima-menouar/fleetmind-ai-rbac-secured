import { FormEvent, useEffect, useRef, useState } from "react";
import { sendMessage } from "../api/chat";
import type { Bot } from "../api/types";
import { readActiveBot, saveActiveBot } from "../store";
import Icon from "./Icon";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

interface ChatWindowProps {
  bots: Bot[];
  initialBotId?: string;
  readOnly?: boolean;
}

const suggestions = [
  "Which vehicles need maintenance this week?",
  "Help me triage a battery warning",
  "Summarize the fleet availability risks",
];

export default function ChatWindow({ bots, initialBotId, readOnly = false }: ChatWindowProps) {
  const [botId, setBotId] = useState(
    initialBotId ?? readActiveBot() ?? bots[0]?.id ?? "technician",
  );
  const [conversationId, setConversationId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string>();
  const messagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const requestedBot = initialBotId
      ? bots.find((bot) => bot.id === initialBotId)
      : undefined;
    const nextBot = requestedBot?.id ?? (bots.some((bot) => bot.id === botId) ? botId : bots[0]?.id);
    if (nextBot && nextBot !== botId) {
      setBotId(nextBot);
      saveActiveBot(nextBot);
    }
  }, [botId, bots, initialBotId]);

  useEffect(() => {
    const container = messagesRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: messages.length ? "smooth" : "auto" });
    }
  }, [messages, isSending]);

  const submit = async (event?: FormEvent) => {
    event?.preventDefault();
    const content = draft.trim();
    if (!content || isSending || readOnly) return;

    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content },
    ]);
    setDraft("");
    setError(undefined);
    setIsSending(true);
    try {
      const response = await sendMessage(content, botId, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.content,
          sources: response.sources,
        },
      ]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The assistant is unavailable.");
    } finally {
      setIsSending(false);
    }
  };

  const chooseSuggestion = (suggestion: string) => {
    setDraft(suggestion);
  };

  const selectedBot = bots.find((bot) => bot.id === botId);

  return (
    <section className="chat-panel">
      <header className="chat-header">
        <div className="assistant-identity">
          <span className="assistant-orb"><Icon name="sparkles" /></span>
          <div>
            <strong>{selectedBot?.name ?? "FleetMind Assistant"}</strong>
            <small><i /> Online · {selectedBot?.department ?? "operations"}</small>
          </div>
        </div>
        <label className="bot-selector">
          <span className="sr-only">Select assistant</span>
          <select value={botId} onChange={(event) => {
            setBotId(event.target.value);
            saveActiveBot(event.target.value);
          }}>
            {bots.map((bot) => <option key={bot.id} value={bot.id}>{bot.name}</option>)}
          </select>
        </label>
      </header>

      <div className="messages" aria-live="polite" ref={messagesRef}>
        {messages.length === 0 && (
          <div className="chat-welcome">
            <span className="welcome-mark"><Icon name="sparkles" /></span>
            <h2>How can I help your fleet today?</h2>
            <p>Ask about maintenance, vehicle health, operations, or customer proposals.</p>
            <div className="suggestion-grid">
              {suggestions.map((suggestion) => (
                <button key={suggestion} type="button" disabled={readOnly} onClick={() => chooseSuggestion(suggestion)}>
                  {suggestion}<span>↗</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message-row ${message.role}`}>
            <span className="message-avatar">{message.role === "assistant" ? <Icon name="sparkles" /> : "You"}</span>
            <div className="message-bubble">
              <p>{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <small>Sources: {message.sources.join(", ")}</small>
              )}
            </div>
          </div>
        ))}
        {isSending && (
          <div className="message-row assistant">
            <span className="message-avatar"><Icon name="sparkles" /></span>
            <div className="typing"><span /><span /><span /></div>
          </div>
        )}
        {error && <div className="inline-error">{error}</div>}
      </div>

      <form className="composer" onSubmit={submit}>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void submit();
            }
          }}
          placeholder={readOnly ? "Viewer access is read-only" : "Ask FleetMind about your fleet…"}
          disabled={readOnly}
          rows={1}
          maxLength={4000}
        />
        <button type="submit" disabled={readOnly || !draft.trim() || isSending} aria-label="Send message"><Icon name="send" /></button>
        <small>{readOnly ? "Viewer role · conversation actions are disabled." : "Demo responses are deterministic. Verify safety-critical recommendations."}</small>
      </form>
    </section>
  );
}
