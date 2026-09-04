import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import ChatPage from "./pages/ChatPage";
import FleetDashboardPage from "./pages/FleetDashboardPage";
import PredictiveMaintenancePage from "./pages/PredictiveMaintenancePage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProtectedRoute from "./components/ProtectedRoute";
import AccessDeniedPage from "./pages/AccessDeniedPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import BotBuilderPage from "./pages/BotBuilderPage";
import MarketplacePage from "./pages/MarketplacePage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/fleet" element={<FleetDashboardPage />} />
            <Route path="/access-denied" element={<AccessDeniedPage />} />
            <Route element={<ProtectedRoute allowedRoles={["admin", "technician"]} />}>
              <Route path="/assistant" element={<ChatPage />} />
              <Route path="/predictive-maintenance" element={<PredictiveMaintenancePage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
            </Route>
            <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
              <Route path="/bots/new" element={<BotBuilderPage />} />
              <Route path="/admin" element={<AdminDashboardPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
