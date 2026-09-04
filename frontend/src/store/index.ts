const ACTIVE_BOT_KEY = "fleetmind.activeBot";

export function readActiveBot(): string | null {
  return window.localStorage.getItem(ACTIVE_BOT_KEY);
}

export function saveActiveBot(botId: string): void {
  window.localStorage.setItem(ACTIVE_BOT_KEY, botId);
}
