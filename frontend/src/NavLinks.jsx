import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

function useMe() {
  const [me, setMe] = useState(null);
  useEffect(() => {
    fetch("/api/auth/me")
      .then(r => r.ok ? r.json() : null)
      .then(setMe)
      .catch(() => setMe(null));
  }, []);
  return me;
}

function NavItem({ to, label }) {
  const loc = useLocation();
  const active = loc.pathname === to || loc.pathname.startsWith(to + "/");
  return (
    <Link
      to={to}
      style={{
        display: "block",
        padding: "10px 12px",
        borderRadius: 12,
        textDecoration: "none",
        color: active ? "white" : "#111",
        background: active ? "#111" : "transparent",
        border: "1px solid " + (active ? "#111" : "transparent"),
      }}
    >
      {label}
    </Link>
  );
}

export default function NavLinks() {
  const me = useMe();
  const role = me?.role || "";

  // Tenants should only see tenant portal
  if (role === "tenant") {
    return (
      <div style={{ display: "grid", gap: 8 }}>
        <NavItem to="/tenant" label="Tenant Portal" />
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <NavItem to="/properties" label="Properties" />
      <NavItem to="/units" label="Units" />
      <NavItem to="/tenants" label="Tenants" />
      <NavItem to="/leases" label="Leases" />
      <NavItem to="/payments" label="Payments" />
      <NavItem to="/maintenance" label="Maintenance" />
      <NavItem to="/billing" label="Billing" />
      <NavItem to="/users" label="Users" />
    </div>
  );
}
