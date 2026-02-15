import React, { useEffect } from "react";

export default function LandingPage() {
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/auth/me", { credentials: "include" });
        const j = await r.json().catch(() => null);
        if (r.ok && j?.role === "tenant") {
          window.location.replace("/tenant");
          return;
        }
        // landlord/staff/owner default
        window.location.replace("/properties");
      } catch {
        window.location.replace("/login");
      }
    })();
  }, []);

  return <div style={{ padding: 16 }}>Loading…</div>;
}
