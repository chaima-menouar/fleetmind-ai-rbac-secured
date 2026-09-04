const ACCESS_TOKEN_KEY = "fleetmind.access-token";
let memoryToken: string | undefined;

export function readAccessToken(): string | undefined {
  try {
    return memoryToken ?? sessionStorage.getItem(ACCESS_TOKEN_KEY) ?? undefined;
  } catch {
    return memoryToken;
  }
}

export function saveAccessToken(token: string): void {
  memoryToken = token;
  try {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
  } catch {
    // The signed session remains available in memory for this page lifecycle.
  }
}

export function clearAccessToken(): void {
  memoryToken = undefined;
  try {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  } catch {
    // The in-memory authentication state is still cleared by AuthContext.
  }
}
