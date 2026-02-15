import React, { useState } from "react";

export default function InviteTenantsPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErr(""); setMsg(""); setLoading(true);
    try {
      const r = await fetch("/api/invites", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const j = await r.json().catch(() => null);
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));

      const url = j.invite_url || "";
      const full = window.location.origin + url;
      setMsg(`Invite created: ${full}`);
      setEmail("");
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 720 }}>
      <h2 style={{ marginTop: 0 }}>Invite tenants</h2>

      {err && <div style={{ background:"#ffe9e9", border:"1px solid #ffb3b3", padding:10, borderRadius:10, marginBottom:12 }}>{err}</div>}
      {msg && <div style={{ background:"#e9fff1", border:"1px solid #b3ffd0", padding:10, borderRadius:10, marginBottom:12 }}>{msg}</div>}

      <form onSubmit={submit} style={{ border:"1px solid #eee", borderRadius:14, padding:14 }}>
        <label style={{ display:"block", marginBottom:10 }}>
          <div style={{ fontSize:12, opacity:0.8, marginBottom:4 }}>Tenant email</div>
          <input value={email} onChange={(e)=>setEmail(e.target.value)}
            style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd" }} />
        </label>
        <button disabled={loading || !email.trim()}
          style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #ddd", background:"#111", color:"white", cursor:"pointer" }}>
          {loading ? "Creating…" : "Create invite link"}
        </button>
      </form>
    </div>
  );
}
