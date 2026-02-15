import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const TOKEN_KEY = "hr_token";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("My Rentals");
  const [mode, setMode] = useState("login"); // login | bootstrap
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const nav = useNavigate();
  const loc = useLocation();
  const next = new URLSearchParams(loc.search).get("next") || "/";

  async function submit(e) {
    e.preventDefault();
    setErr(""); setMsg(""); setLoading(true);
    try {
      const url = mode === "bootstrap" ? "/api/auth/bootstrap" : "/api/auth/login";
      const body = mode === "bootstrap" ? { org_name: orgName, email, password } : { email, password };

      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json().catch(() => null);

      if (!r.ok) {
        if (r.status === 409 && mode === "bootstrap") {
          setMode("login");
          setMsg("Already initialized. Please login.");
          return;
        }
        throw new Error(data?.detail || JSON.stringify(data) || `HTTP ${r.status}`);
      }

      localStorage.setItem(TOKEN_KEY, data.access_token);

      // Redirect: tenants go to portal
      if (data.role === "tenant") nav("/tenant", { replace: true });
      else nav(next, { replace: true });
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", padding: 16 }}>
      <div className="hr-card">
        <div className="hr-top">
          <div className="hr-title">HappyRentals</div>
          <div className="hr-pill">SaaS</div>
        </div>

        <div style={{ display:"flex", gap:8, marginBottom:12 }}>
          <button className={"hr-btn " + (mode==="login" ? "hr-btn-primary":"")} onClick={() => setMode("login")}>Login</button>
          <button className={"hr-btn " + (mode==="bootstrap" ? "hr-btn-primary":"")} onClick={() => setMode("bootstrap")}>Create first account</button>
        </div>

        {msg && <div className="hr-alert ok" style={{ marginBottom:12 }}>{msg}</div>}
        {err && <div className="hr-alert err" style={{ marginBottom:12 }}>{err}</div>}

        <form onSubmit={submit}>
          {mode === "bootstrap" && (
            <>
              <div className="hr-label">Organization name</div>
              <input className="hr-input" value={orgName} onChange={(e)=>setOrgName(e.target.value)} />
            </>
          )}

          <div className="hr-label">Email</div>
          <input className="hr-input" value={email} onChange={(e)=>setEmail(e.target.value)} />

          <div className="hr-label">Password</div>
          <input className="hr-input" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />

          <div style={{ marginTop:12 }}>
            <button className="hr-btn hr-btn-primary" disabled={loading} style={{ width:"100%" }}>
              {loading ? "Working…" : (mode==="bootstrap" ? "Create account" : "Login")}
            </button>
          </div>
        </form>

        <div style={{ fontSize:12, color:"var(--muted)", marginTop:12 }}>
          If you were invited as a tenant, use the invite link first.
        </div>
      </div>
    </div>
  );
}
