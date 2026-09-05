import { apiFetch } from "./client";
import type { AuthSession, CurrentUser } from "./types";

interface ApiMessage {
  message: string;
}

export function loginWithPassword(email: string, password: string) {
  return apiFetch<AuthSession>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function startViewerRegistration(displayName: string, email: string, password: string) {
  return apiFetch<ApiMessage>("/api/auth/register-viewer/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      display_name: displayName,
      email,
      password,
    }),
  });
}

export function confirmViewerRegistration(email: string, verificationCode: string) {
  return apiFetch<ApiMessage>("/api/auth/register-viewer/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      verification_code: verificationCode,
    }),
  });
}

export function getCurrentUser() {
  return apiFetch<CurrentUser>("/api/auth/me");
}
