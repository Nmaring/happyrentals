import React, { useMemo, useState } from "react";

export default function AcceptInvitePage() {
  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const token = params.get("token") || "";

  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const r = await fetch("/api/invites/accept", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      const j = await r.json().catch(() => null);
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setDone(true);
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Accept invite</h2>

      {!token && (
        <div style={{ background:"#ffe9e9", border:"1px solid #ffb3b3", padding:10, borderRadius:10 }}>
          Missing invite token.
        </div>
      )}

      {err && (
        <div style={{ background:"#ffe9e9", border:"1px solid #ffb3b3", padding:10, borderRadius:10, marginTop:12 }}>
          {err}
        </div>
      )}

      {done ? (
        <div style={{ border:"1px solid #eee", borderRadius:14, padding:14, marginTop:12 }}>
          ✅ Password set. You can now <a href="/login">login</a>.
        </div>
      ) : (
        <form onSubmit={submit} style={{ border:"1px solid #eee", borderRadius:14, padding:14, marginTop:12 }}>
          <div style={{ fontSize:12, opacity:0.7, marginBottom:8 }}>
            Set a password for your tenant account.
          </div>

          <label style={{ display:"block", marginBottom:10 }}>
            <div style={{ fontSize:12, opacity:0.8, marginBottom:4 }}>Password</div>
            <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)}
              style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd" }} />
          </label>

          <button disabled={loading || !token || password.length < 8}
            style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd", background:"#111", color:"white", cursor:"pointer" }}>
            {loading ? "Working…" : "Accept invite"}
          </button>
        </form>
      )}
    </div>
  );
}
