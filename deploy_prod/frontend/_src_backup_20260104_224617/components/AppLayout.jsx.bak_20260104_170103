import React from "react";
import { NavLink, Outlet } from "react-router-dom";

const linkStyle = ({ isActive }) => ({
  display: "block",
  padding: "10px 12px",
  borderRadius: 10,
  textDecoration: "none",
  color: isActive ? "white" : "#111827",
  background: isActive ? "#111827" : "transparent",
});

export default function AppLayout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f3f4f6" }}>
      <aside style={{ width: 240, padding: 14, background: "white", borderRight: "1px solid #e5e7eb" }}>
        <div style={{ fontWeight: 800, fontSize: 18, padding: "6px 8px 14px" }}>HappyRentals</div>
        <nav style={{ display: "grid", gap: 6 }}>
          <NavLink to="/properties" style={linkStyle}>Properties</NavLink>
          <NavLink to="/units" style={linkStyle}>Units</NavLink>
          <NavLink to="/tenants" style={linkStyle}>Tenants</NavLink>
          <NavLink to="/leases" style={linkStyle}>Leases</NavLink>
          <NavLink to="/payments" style={linkStyle}>Payments</NavLink>
        </nav>
      </aside>

      <main style={{ flex: 1, padding: 16 }}>
        <Outlet />
      </main>
    </div>
  );
}

