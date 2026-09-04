import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth, type UserRole } from "../hooks/AuthContext";

export default function ProtectedRoute({ allowedRoles }: { allowedRoles?: UserRole[] }) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();
  if (isLoading) return <div className="app-loading">Validating your secure session…</div>;
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  if (allowedRoles && (!user || !allowedRoles.includes(user.role))) {
    return <Navigate to="/access-denied" replace />;
  }
  return <Outlet />;
}
