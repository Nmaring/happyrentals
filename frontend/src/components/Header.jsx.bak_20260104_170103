import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../providers/AuthProvider";
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Header() {
  const { token, user, logout } = useAuth();
  const [apiOk, setApiOk] = useState(null); // null | true | false
  const loc = useLocation();
  const nav = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function ping() {
      try {
        await api.health();
        if (!cancelled) setApiOk(true);
      } catch {
        if (!cancelled) setApiOk(false);
      }
    }

    ping();
    const t = setInterval(ping, 4000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, []);

  function doLogout() {
    logout();
    // keep it predictable
    nav("/login");
  }

  const dotColor = apiOk === null ? "rgba(255,255,255,0.35)" : apiOk ? "#22c55e" : "#ef4444";

  return (
    <div
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(10px)",
        background: "rgba(11,15,25,0.7)",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
      <div
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "12px 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
        <Link to="/" style={{ fontWeight: 900, letterSpacing: "-0.02em" }}>
          HappyRentals
        </Link>

        <nav style={{ display: "flex", gap: 10, marginLeft: 8 }}>
          <NavLink to="/properties" active={loc.pathname.startsWith("/properties")}>
            Properties
          </NavLink>
          <NavLink to="/units" active={loc.pathname.startsWith("/units")}>
            Units
          </NavLink>
          <NavLink to="/tenants" active={loc.pathname.startsWith("/tenants")}>
            Tenants
          </NavLink>
        </nav>

        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              title={apiOk === null ? "Checking APIâ€¦" : apiOk ? "API Online" : "API Offline"}
              style={{
                width: 10,
                height: 10,
                borderRadius: 999,
                background: dotColor,
                boxShadow: `0 0 0 3px rgba(255,255,255,0.06)`,
              }}
            />
            <span style={{ fontSize: 13, color: "rgba(255,255,255,0.7)" }}>
              {apiOk === null ? "APIâ€¦" : apiOk ? "API OK" : "API Down"}
            </span>
          </div>

          {token ? (
            <>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.75)" }}>
                {user?.email || "Logged in"}
              </div>
              <button className="btn" onClick={doLogout}>
                Logout
              </button>
            </>
          ) : (
            <Link className="btn primary" to="/login">
              Login
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

function NavLink({ to, active, children }) {
  return (
    <Link
      to={to}
      style={{
        padding: "6px 10px",
        borderRadius: 10,
        border: active ? "1px solid rgba(255,255,255,0.16)" : "1px solid transparent",
        background: active ? "rgba(255,255,255,0.06)" : "transparent",
        color: "rgba(255,255,255,0.85)",
        fontSize: 13,
        fontWeight: 800,
      }}
      {children}
    </Link>
  );
}

