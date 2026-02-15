import React, { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const TOKEN_KEY = "hr_token";

function NavItem({ to, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => "hr-link" + (isActive ? " active" : "")}
    >
      {label}
    </NavLink>
  );
}

export default function AppLayout() {
  const [me, setMe] = useState(null);

  useEffect(() => {
    (async () => {
      const r = await fetch("/api/auth/me");
      if (r.ok) setMe(await r.json());
    })();
  }, []);

  async function logout() {
    try { await fetch("/api/auth/logout", { method: "POST" }); } catch {}
    try { localStorage.removeItem(TOKEN_KEY); } catch {}
    window.location.replace("/login");
  }

  const role = (me?.role || "").toLowerCase();
  const email = me?.email || "";

  return (
    <div className="hr-layout">
      <aside className="hr-sidebar">
        <div className="hr-top">
          <div className="hr-title">HappyRentals</div>
        </div>

        <div className="hr-pill">{email || "…"}</div>
        <div className="hr-pill" style={{ marginTop:8 }}>role: {role || "…"}</div>

        <div className="hr-nav">
          {role === "tenant" ? (
            <>
              <NavItem to="/tenant" label="Tenant Portal" />
              <NavItem to="/maintenance" label="Maintenance" />
            </>
          ) : (
            <>
              <NavItem to="/properties" label="Properties" />
              <NavItem to="/units" label="Units" />
              <NavItem to="/tenants" label="Tenants" />
              <NavItem to="/invite-tenants" label="Invite Tenants" />
              <NavItem to="/leases" label="Leases" />
              <NavItem to="/payments" label="Payments" />
              <NavItem to="/maintenance" label="Maintenance" />
              <NavItem to="/billing" label="Billing" />
            </>
          )}
        </div>

        <div style={{ marginTop:14 }}>
          <button className="hr-btn hr-btn-danger" onClick={logout} style={{ width:"100%" }}>
            Logout
          </button>
        </div>
      </aside>

      <main className="hr-main">
        <Outlet />
      </main>
    </div>
  );
}
