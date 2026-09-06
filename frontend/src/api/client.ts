import { clearAccessToken, readAccessToken } from "../auth/session";

const CONFIGURED_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const API_BASE_URL = import.meta.env.DEV ? CONFIGURED_BASE_URL : "";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

async function fetchApi(path: string, options: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, options);
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20_000);
  try {
    const accessToken = readAccessToken();
    const headers = new Headers(options?.headers);
    if (!headers.has("Accept")) headers.set("Accept", "application/json");
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

    const response = await fetchApi(path, {
      ...options,
      signal: controller.signal,
      headers,
    });

    if (!response.ok) {
      const body = (await response.json().catch(() => null)) as { detail?: string } | null;
      const detail = body?.detail ?? `Request failed (${response.status})`;
      const invalidSession =
        response.status === 401 &&
        /session|token|expired|valid session|verified session/i.test(detail);

      if (invalidSession && !path.startsWith("/api/auth/")) {
        clearAccessToken();
        window.dispatchEvent(new Event("fleetmind:unauthorized"));
      }
      throw new ApiError(detail, response.status);
    }
    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeout);
  }
}
