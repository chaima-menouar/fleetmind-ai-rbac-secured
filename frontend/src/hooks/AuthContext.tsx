import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  confirmViewerRegistration,
  getCurrentUser,
  loginWithPassword,
  startViewerRegistration,
} from "../api/auth";
import type { CurrentUser } from "../api/types";
import { clearAccessToken, readAccessToken, saveAccessToken } from "../auth/session";

export type { CurrentUser, UserRole } from "../api/types";

interface AuthContextValue {
  user?: CurrentUser;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<CurrentUser>;
  requestViewerCode: (name: string, email: string, password: string) => Promise<void>;
  createViewer: (
    email: string,
    password: string,
    verificationCode: string,
  ) => Promise<CurrentUser>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser>();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!readAccessToken()) {
      setIsLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => clearAccessToken())
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => setUser(undefined);
    window.addEventListener("fleetmind:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("fleetmind:unauthorized", handleUnauthorized);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    login: async (email, password) => {
      const session = await loginWithPassword(email.trim().toLowerCase(), password);
      saveAccessToken(session.access_token);
      setUser(session.user);
      return session.user;
    },
    requestViewerCode: async (name, email, password) => {
      await startViewerRegistration(
        name.trim(),
        email.trim().toLowerCase(),
        password,
      );
    },
    createViewer: async (email, password, verificationCode) => {
      const normalizedEmail = email.trim().toLowerCase();
      await confirmViewerRegistration(normalizedEmail, verificationCode);
      const session = await loginWithPassword(normalizedEmail, password);
      saveAccessToken(session.access_token);
      setUser(session.user);
      return session.user;
    },
    logout: () => {
      clearAccessToken();
      setUser(undefined);
    },
  }), [isLoading, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
