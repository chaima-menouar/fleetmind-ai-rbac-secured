import { clearAccessToken, readAccessToken } from "../auth/session";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20_000);
  try {
    const accessToken = readAccessToken();
    const headers = new Headers(options?.headers);
    if (!headers.has("Accept")) headers.set("Accept", "application/json");
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    const response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers,
    });
    if (!response.ok) {
      if (response.status === 401 && !path.startsWith("/api/auth/")) {
        clearAccessToken();
        window.dispatchEvent(new Event("fleetmind:unauthorized"));
      }
      const body = (await response.json().catch(() => null)) as { detail?: string } | null;
      throw new ApiError(body?.detail ?? `Request failed (${response.status})`, response.status);
    }
    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeout);
  }
}
