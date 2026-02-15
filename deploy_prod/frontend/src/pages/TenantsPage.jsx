import React, { useEffect, useState } from "react";
import { unwrapList } from "../utils/unwrapList";

const API = import.meta.env.VITE_API_URL || "/api";

function emptyTenant() {
  return { first_name: "", last_name: "", email: "", phone: "", notes: "" };
}

function genPass() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$";
  let out = "";
  for (let i = 0; i < 14; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function Field({ label, value, onChange, placeholder, type = "text" }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <input
        type={type}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || ""}
        style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", outline: "none" }}
      />
    </label>
  );
}

function TextArea({ label, value, onChange, placeholder }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <textarea
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || ""}
        rows={4}
        style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", outline: "none", resize: "vertical" }}
      />
    </label>
  );
}

export default function TenantsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyTenant());

  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteTenant, setInviteTenant] = useState(null);
  const [inviteEmail, setInviteEmail] = useState("");
  const [invitePass, setInvitePass] = useState("");

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const r = await fetch(`${API}/tenants`);
      const j = await r.json();
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setItems(unwrapList(j));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function startAdd() {
    setEditing(null);
    setForm(emptyTenant());
    setOpen(true);
  }

  function startEdit(t) {
    setEditing(t);
    setForm({
      first_name: t?.first_name ?? "",
      last_name: t?.last_name ?? "",
      email: t?.email ?? "",
      phone: t?.phone ?? "",
      notes: t?.notes ?? "",
    });
    setOpen(true);
  }

  async function save(e) {
    e?.preventDefault?.();
    setSaving(true);
    setErr("");

    const isEdit = Boolean(editing?.id);
    const url = isEdit ? `${API}/tenants/${editing.id}` : `${API}/tenants`;
    const method = isEdit ? "PUT" : "POST";

    const payload = {
      first_name: (form.first_name || "").trim(),
      last_name: (form.last_name || "").trim(),
      email: (form.email || "").trim() || null,
      phone: (form.phone || "").trim() || null,
      notes: (form.notes || "").trim() || null,
    };

    if (!payload.first_name || !payload.last_name) {
      setErr("First name and last name are required.");
      setSaving(false);
      return;
    }

    try {
      const r = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await r.json().catch(() => null);
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j) || `HTTP ${r.status}`);
      setOpen(false);
      await load();
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setSaving(false);
    }
  }

  async function remove(t) {
    if (!t?.id) return;
    if (!confirm(`Delete tenant #${t.id}?`)) return;
    setErr("");
    try {
      const r = await fetch(`${API}/tenants/${t.id}`, { method: "DELETE" });
      const j = await r.json().catch(() => null);
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j) || `HTTP ${r.status}`);
      await load();
    } catch (e) {
      setErr(String(e));
    }
  }

  function startInvite(t) {
    setInviteTenant(t);
    setInviteEmail((t?.email || "").trim() || "tenant@example.com");
    setInvitePass(genPass());
    setInviteOpen(true);
  }

  async function doInvite(e) {
    e?.preventDefault?.();
    setErr("");
    try {
      if (!inviteTenant?.id) throw new Error("Missing tenant_id");
      const payload = { tenant_id: inviteTenant.id, email: inviteEmail.trim(), password: invitePass };

      const r = await fetch(`${API}/users/invite-tenant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await r.json().catch(() => null);
      if (!r.ok) throw new Error(j?.detail || JSON.stringify(j) || `HTTP ${r.status}`);

      const loginUrl = `${window.location.origin}/login`;
      const clip = `Tenant login created:\nEmail: ${inviteEmail}\nPassword: ${invitePass}\nLogin: ${loginUrl}`;

      try {
        await navigator.clipboard.writeText(clip);
        alert("Tenant login created. Credentials copied to clipboard.");
      } catch {
        alert(clip);
      }

      setInviteOpen(false);
      await load(); // refresh tenant list (email may get updated)
    } catch (e2) {
      setErr(String(e2));
    }
  }

  function displayName(t) {
    const full = `${t?.first_name || ""} ${t?.last_name || ""}`.trim();
    return full || t?.email || `Tenant #${t?.id}`;
  }

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Tenants</h2>
        <button
          onClick={startAdd}
          style={{ marginLeft: "auto", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          + Add Tenant
        </button>
      </div>

      {err && (
        <div style={{ background: "#ffe9e9", border: "1px solid #ffb3b3", padding: 10, borderRadius: 10, marginBottom: 12 }}>
          {err}
        </div>
      )}

      {loading ? (
        <div>Loading…</div>
      ) : (
        <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#fafafa" }}>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Name</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Email</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Phone</th>
                <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((t) => (
                <tr key={t.id}>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{displayName(t)}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{t.email || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{t.phone || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2", textAlign: "right" }}>
                    <button
                      onClick={() => startEdit(t)}
                      style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", marginRight: 8 }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => startInvite(t)}
                      style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", marginRight: 8 }}
                    >
                      Invite Login
                    </button>
                    <button
                      onClick={() => remove(t)}
                      style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #f1b3b3", background: "#fff5f5", cursor: "pointer" }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ padding: 14, opacity: 0.7 }}>
                    No tenants yet. Click “Add Tenant”.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Add/Edit modal */}
      {open && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}
          onClick={() => !saving && setOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={save}
            style={{ width: "min(720px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>{editing ? "Edit Tenant" : "Add Tenant"}</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setOpen(false)} disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit" disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="First name" value={form.first_name} onChange={(v) => setForm({ ...form, first_name: v })} />
              <Field label="Last name" value={form.last_name} onChange={(v) => setForm({ ...form, last_name: v })} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} placeholder="tenant@example.com" />
              <Field label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
            </div>

            <TextArea label="Notes" value={form.notes} onChange={(v) => setForm({ ...form, notes: v })} placeholder="optional" />
          </form>
        </div>
      )}

      {/* Invite modal */}
      {inviteOpen && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}
          onClick={() => setInviteOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={doInvite}
            style={{ width: "min(720px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>Invite Tenant Login</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setInviteOpen(false)}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit"
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  Create Login
                </button>
              </div>
            </div>

            <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
              Creates a tenant login and copies credentials. Tenants do not pay.
            </div>

            <label style={{ display: "block", marginBottom: 10 }}>
              <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>Tenant</div>
              <div style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #eee", background: "#fafafa" }}>
                #{inviteTenant?.id} — {displayName(inviteTenant)}
              </div>
            </label>

            <Field label="Login email" value={inviteEmail} onChange={setInviteEmail} placeholder="tenant@example.com" />
            <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
              <div style={{ flex: 1 }}>
                <Field label="Temporary password" value={invitePass} onChange={setInvitePass} />
              </div>
              <button type="button" onClick={() => setInvitePass(genPass())}
                style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", height: 42 }}>
                Regenerate
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
