import React, { useEffect, useState } from "react";

export default function SubscriptionBanner() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const r = await fetch("/api/billing/usage", { credentials: "include" });
        const j = await r.json().catch(() => null);
        if (!alive) return;
        if (r.ok) setInfo(j);
      } catch {}
    })();
    return () => { alive = false; };
  }, []);

  const status = info?.status;
  if (!status) return null;

  if (status === "active" || status === "trialing") return null;

  return (
    <div style={{
      margin: "12px 16px",
      padding: 12,
      borderRadius: 12,
      border: "1px solid #ffd3a3",
      background: "#fff7ed",
      display: "flex",
      alignItems: "center",
      gap: 12,
    }}>
      <div style={{ fontWeight: 700 }}>Subscription required</div>
      <div style={{ opacity: 0.8 }}>Status: {status}. Your account is read-only until you subscribe.</div>
      <button
        onClick={() => (window.location.href = "/billing")}
        style={{ marginLeft: "auto", padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}
      >
        Go to Billing
      </button>
    </div>
  );
}
