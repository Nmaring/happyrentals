import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import AuthGate from "./auth/AuthGate.jsx";

import LoginPage from "./pages/LoginPage.jsx";
import AcceptInvitePage from "./pages/AcceptInvitePage.jsx";
import InviteTenantsPage from "./pages/InviteTenantsPage.jsx";

import DashboardPage from "./pages/DashboardPage.jsx";
import PropertiesPage from "./pages/PropertiesPage.jsx";
import UnitsPage from "./pages/UnitsPage.jsx";
import TenantsPage from "./pages/TenantsPage.jsx";
import LeasesPage from "./pages/LeasesPage.jsx";
import PaymentsPage from "./pages/PaymentsPage.jsx";
import BillingPage from "./pages/BillingPage.jsx";
import MaintenancePage from "./pages/MaintenancePage.jsx";
import TenantPortalPage from "./pages/TenantPortalPage.jsx";

export default function App(){
  return (
    <Routes>
      <Route path="/login" element={<LoginPage/>} />
      <Route path="/accept-invite" element={<AcceptInvitePage/>} />

      <Route path="/*" element={<AuthGate><AppLayout/></AuthGate>}>
        <Route index element={<DashboardPage/>} />
        <Route path="properties" element={<PropertiesPage/>} />
        <Route path="units" element={<UnitsPage/>} />
        <Route path="tenants" element={<TenantsPage/>} />
        <Route path="invite-tenants" element={<InviteTenantsPage/>} />
        <Route path="leases" element={<LeasesPage/>} />
        <Route path="payments" element={<PaymentsPage/>} />
        <Route path="maintenance" element={<MaintenancePage/>} />
        <Route path="billing" element={<BillingPage/>} />
        <Route path="tenant" element={<TenantPortalPage/>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
