import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>HappyRentals</h2>
        <button onClick={logout}>Logout</button>
      </div>

      <div style={{ marginTop: 8 }}>
        Signed in as: <b>{user?.email}</b>
      </div>

      <hr style={{ margin: "20px 0" }} />

      <div style={{ display: "grid", gap: 10 }}>
        <Link to="/properties">Go to Properties</Link>

        <div style={{ color: "#555" }}>
          Next steps:
          <ul>
            <li><b>Step 2:</b> Properties (you are here)</li>
            <li><b>Step 3:</b> Units</li>
            <li><b>Step 4:</b> Tenants</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
