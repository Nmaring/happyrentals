import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const actions = [
  { label: "Property", route: "/properties" },
  { label: "Tenant", route: "/tenants" },
  { label: "Unit", route: "/units" },
  { label: "Lease", route: "/leases" },
  { label: "Payment", route: "/payments" },
];

export default function QuickAdd() {
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const loc = useLocation();

  function go(route) {
    setOpen(false);
    if (loc.pathname !== route) {
      nav(`${route}?new=1`);
    } else {
      // same page: just add ?new=1 so the page opens its modal
      nav(`${route}?new=1`, { replace: false });
    }
  }

  return (
    <div style={{ position: "fixed", right: 16, bottom: 16, zIndex: 9999 }}>
      {open && (
        <div
          style={{
            marginBottom: 10,
            background: "white",
            border: "1px solid #eee",
            borderRadius: 14,
            boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
            overflow: "hidden",
            width: 220,
          }}
        >
          {actions.map((a) => (
            <button
              key={a.route}
              onClick={() => go(a.route)}
              style={{
                width: "100%",
                textAlign: "left",
                padding: "10px 12px",
                border: "none",
                borderBottom: "1px solid #f2f2f2",
                background: "white",
                cursor: "pointer",
              }}
            >
              + {a.label}
            </button>
          ))}
          <button
            onClick={() => setOpen(false)}
            style={{
              width: "100%",
              textAlign: "left",
              padding: "10px 12px",
              border: "none",
              background: "#fafafa",
              cursor: "pointer",
            }}
          >
            Close
          </button>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        title="Quick Add"
        style={{
          width: 54,
          height: 54,
          borderRadius: 999,
          border: "1px solid #ddd",
          background: "#111",
          color: "white",
          fontSize: 24,
          cursor: "pointer",
          boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
        }}
      >
        +
      </button>
    </div>
  );
}

