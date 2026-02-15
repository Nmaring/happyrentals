import React, { useEffect, useState } from "react";

export default function UsersPage() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("manager");
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const r = await fetch("/api/users", { credentials: "include" });
      const j = await r.json();
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setItems(j || []);
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function create(e) {
    e.preventDefault();
    setSaving(true);
    setErr("");
    try {
      const r = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password, role }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setEmail(""); setPassword(""); setRole("manager");
      await load();
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setSaving(false);
    }
  }

  async function deactivate(id) {
    if (!confirm("Deactivate this user?")) return;
    setErr("");
    try {
      const r = await fetch(`/api/users/${id}/deactivate`, { method: "PUT", credentials: "include" });
      const j = await r.json();
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      await load();
    } catch (e) {
      setErr(String(e));
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Users</h2>

      {err && (
        <div style={{ background: "#ffe9e9", border: "1px solid #ffb3b3", padding: 10, borderRadius: 10, marginBottom: 12 }}>
          {err}
        </div>
      )}

      <form onSubmit={create} style={{ border: "1px solid #eee", borderRadius: 14, padding: 14, marginBottom: 12 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Create a team login</div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12 }}>
          <label>
            <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Email</div>
            <input value={email} onChange={(e)=>setEmail(e.target.value)} style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd" }} />
          </label>

          <label>
            <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Role</div>
            <select value={role} onChange={(e)=>setRole(e.target.value)} style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd", background:"white" }}>
              <option value="manager">manager</option>
              <option value="staff">staff</option>
              <option value="tenant">tenant</option>
            </select>
          </label>

          <label>
            <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Password</div>
            <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} style={{ width:"100%", padding:"10px 12px", borderRadius:10, border:"1px solid #ddd" }} />
          </label>
        </div>

        <div style={{ marginTop: 10, display:"flex", gap: 10 }}>
          <button disabled={saving || !email || !password} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #ddd", background:"#111", color:"white", cursor:"pointer" }}>
            {saving ? "Creating…" : "Create user"}
          </button>
          <button type="button" onClick={load} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #ddd", background:"white", cursor:"pointer" }}>
            Refresh
          </button>
        </div>
      </form>

      {loading ? (
        <div>Loading…</div>
      ) : (
        <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#fafafa" }}>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Email</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Role</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Active</th>
                <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(u => (
                <tr key={u.id}>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.email}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.role}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.is_active ? "yes" : "no"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2", textAlign: "right" }}>
                    {u.role !== "owner" && u.is_active && (
                      <button onClick={() => deactivate(u.id)} style={{ padding:"8px 10px", borderRadius:10, border:"1px solid #f1b3b3", background:"#fff5f5", cursor:"pointer" }}>
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={4} style={{ padding: 14, opacity: 0.7 }}>No users found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
