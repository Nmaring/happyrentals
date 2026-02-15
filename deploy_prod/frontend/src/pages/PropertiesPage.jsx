import React, { useEffect, useState } from "react";
import { unwrapList } from "../utils/unwrapList";

const API = import.meta.env.VITE_API_URL || "/api";

function emptyForm() {
  return {
    name: "",
    address1: "",
    address2: "",
    city: "",
    state: "",
    zip: "",
    notes: "",
  };
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <input
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || ""}
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid #ddd",
          outline: "none",
        }}
      />
    </label>
  );
}

function TextArea({ label, value, onChange, placeholder }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <textarea
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || ""}
        rows={4}
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid #ddd",
          outline: "none",
          resize: "vertical",
        }}
      />
    </label>
  );
}

export default function PropertiesPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null); // property object or null
  const [form, setForm] = useState(emptyForm());

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const r = await fetch(`${API}/properties`);
      const data = await r.json();
      setItems(unwrapList(data));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startAdd() {
    setEditing(null);
    setForm(emptyForm());
    setOpen(true);
  }

  function startEdit(p) {
    setEditing(p);
    setForm({
      name: p?.name || "",
      address1: p?.address1 || "",
      address2: p?.address2 || "",
      city: p?.city || "",
      state: p?.state || "",
      zip: p?.zip || "",
      notes: p?.notes || "",
    });
    setOpen(true);
  }

  async function save(e) {
    e?.preventDefault?.();
    setSaving(true);
    setErr("");

    const isEdit = Boolean(editing?.id);
    const url = isEdit ? `${API}/properties/${editing.id}` : `${API}/properties`;
    const method = isEdit ? "PUT" : "POST";

    try {
      const r = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!r.ok) {
        const t = await r.text();
        throw new Error(`${method} ${url} failed: ${r.status} ${t}`);
      }

      setOpen(false);
      await load();
    } catch (e) {
      setErr(String(e));
    } finally {
      setSaving(false);
    }
  }

  async function remove(p) {
    if (!p?.id) return;
    if (!confirm(`Delete property #${p.id} "${p.name || ""}"?`)) return;

    setErr("");
    try {
      const r = await fetch(`${API}/properties/${p.id}`, { method: "DELETE" });
      if (!r.ok) {
        const t = await r.text();
        throw new Error(`DELETE failed: ${r.status} ${t}`);
      }
      await load();
    } catch (e) {
      setErr(String(e));
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Properties</h2>
        <button
          onClick={startAdd}
          style={{
            marginLeft: "auto",
            padding: "10px 12px",
            borderRadius: 10,
            border: "1px solid #ddd",
            background: "white",
            cursor: "pointer",
          }}
        >
          + Add Property
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
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Address</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>City</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>State</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Zip</th>
                <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((p) => (
                <tr key={p.id}>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.name || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>
                    {[p.address1, p.address2].filter(Boolean).join(" ")}
                  </td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.city || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.state || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.zip || "-"}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2", textAlign: "right" }}>
                    <button
                      onClick={() => startEdit(p)}
                      style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", marginRight: 8 }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => remove(p)}
                      style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #f1b3b3", background: "#fff5f5", cursor: "pointer" }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: 14, opacity: 0.7 }}>
                    No properties yet. Click “Add Property”.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {open && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
          onClick={() => !saving && setOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={save}
            style={{
              width: "min(720px, 100%)",
              background: "white",
              borderRadius: 14,
              padding: 16,
              boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>{editing ? "Edit Property" : "Add Property"}</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}
                >
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <Field label="Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} placeholder="e.g., 4255 Minnehaha Ave" />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Address 1" value={form.address1} onChange={(v) => setForm({ ...form, address1: v })} />
              <Field label="Address 2" value={form.address2} onChange={(v) => setForm({ ...form, address2: v })} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12 }}>
              <Field label="City" value={form.city} onChange={(v) => setForm({ ...form, city: v })} />
              <Field label="State" value={form.state} onChange={(v) => setForm({ ...form, state: v })} placeholder="MN" />
              <Field label="Zip" value={form.zip} onChange={(v) => setForm({ ...form, zip: v })} />
            </div>
            <TextArea label="Notes" value={form.notes} onChange={(v) => setForm({ ...form, notes: v })} />
          </form>
        </div>
      )}
    </div>
  );
}

