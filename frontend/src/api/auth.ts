import { apiFetch } from "./client";
import type { AuthSession, CurrentUser } from "./types";

export function loginWithPassword(email: string, password: string) {
  return apiFetch<AuthSession>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function registerViewer(
  displayName: string,
  email: string,
  password: string,
  verificationCode: string,
) {
  return apiFetch<AuthSession>("/api/auth/register-viewer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      display_name: displayName,
      email,
      password,
      verification_code: verificationCode,
    }),
  });
}

export function getCurrentUser() {
  return apiFetch<CurrentUser>("/api/auth/me");
}
