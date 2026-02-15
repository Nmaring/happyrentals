import React, { useEffect, useState } from "react";

export default function AuthGate({ children }) {
  const [ok, setOk] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let on = true;
    (async () => {
      try {
        const r = await fetch("/api/auth/me");
        if (on && r.ok) setOk(true);
        if (on && !r.ok) {
          const next = encodeURIComponent(window.location.pathname + window.location.search);
          window.location.replace(`/login?next=${next}`);
        }
      } catch {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.replace(`/login?next=${next}`);
      } finally {
        if (on) setChecking(false);
      }
    })();
    return () => { on = false; };
  }, []);

  if (checking) return <div className="hr-page">Loading…</div>;
  return ok ? children : null;
}
