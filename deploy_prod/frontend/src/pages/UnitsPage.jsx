import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { unwrapList } from "../utils/unwrapList";
import { propertyName, unitName } from "../utils/labels";

const API = import.meta.env.VITE_API_URL || "/api";

function numOrNull(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
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

function Select({ label, value, onChange, options, allLabel = "All" }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", outline: "none", background: "white" }}
      >
        <option value="">{allLabel}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function UnitsPage() {
  const loc = useLocation();
  const nav = useNavigate();

  const [units, setUnits] = useState([]);
  const [properties, setProperties] = useState([]);
  const [knownKeys, setKnownKeys] = useState(new Set());

  const [propertyFilter, setPropertyFilter] = useState("");
  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState({
    property_id: "",
    unit_number: "",
    bedrooms: "",
    bathrooms: "",
    sq_ft: "",
    notes: "",
  });

  const propMap = useMemo(() => new Map(properties.map((p) => [String(p.id), p])), [properties]);

  async function loadAll() {
    setLoading(true);
    setErr("");
    try {
      const [uR, pR] = await Promise.all([fetch(`${API}/units`), fetch(`${API}/properties`)]);
      const uJ = await uR.json();
      const pJ = await pR.json();
      const u = unwrapList(uJ);
      const p = unwrapList(pJ);
      setUnits(u);
      setProperties(p);
      setKnownKeys(new Set(Object.keys(u[0] || {})));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, []);

  function startAdd() {
    setEditing(null);
    setForm({ property_id: "", unit_number: "", bedrooms: "", bathrooms: "", sq_ft: "", notes: "" });
    setOpen(true);
  }

  // QuickAdd support: /units?new=1
  useEffect(() => {
    const qs = new URLSearchParams(loc.search);
    if (qs.get("new") === "1") {
      startAdd();
      nav(loc.pathname, { replace: true });
    }
  }, [loc.search]);

  function startEdit(u) {
    setEditing(u);
    setForm({
      property_id: u?.property_id != null ? String(u.property_id) : "",
      unit_number: u?.unit_number ?? "",
      bedrooms: u?.bedrooms ?? "",
      bathrooms: u?.bathrooms ?? "",
      sq_ft: u?.sq_ft ?? u?.sqft ?? "",
      notes: u?.notes ?? "",
    });
    setOpen(true);
  }

  function buildPayload() {
    const payload = {
      property_id: numOrNull(form.property_id),
      unit_number: form.unit_number?.trim(),
      bedrooms: numOrNull(form.bedrooms),
      bathrooms: numOrNull(form.bathrooms),
      sq_ft: numOrNull(form.sq_ft),
      notes: form.notes?.trim() || null,
    };

    // Only send fields the API already returns (prevents 422 on unknown fields)
    const out = {};
    for (const [k, v] of Object.entries(payload)) {
      if (k === "property_id" || k === "unit_number") out[k] = v;
      else if (knownKeys.has(k)) out[k] = v;
    }
    return out;
  }

  async function save(e) {
    e?.preventDefault?.();
    setSaving(true);
    setErr("");

    const isEdit = Boolean(editing?.id);
    const url = isEdit ? `${API}/units/${editing.id}` : `${API}/units`;
    const method = isEdit ? "PUT" : "POST";

    try {
      const payload = buildPayload();
      const r = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`${method} failed: ${r.status} ${await r.text()}`);
      setOpen(false);
      await loadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setSaving(false);
    }
  }

  async function remove(u) {
    if (!u?.id) return;
    if (!confirm(`Delete unit #${u.id}?`)) return;

    setErr("");
    try {
      const r = await fetch(`${API}/units/${u.id}`, { method: "DELETE" });
      if (!r.ok) throw new Error(`DELETE failed: ${r.status} ${await r.text()}`);
      await loadAll();
    } catch (e) {
      setErr(String(e));
    }
  }

  const propertyOptions = properties.map((p) => ({
    value: String(p.id),
    label: propertyName(p),
  }));

  const filteredUnits = useMemo(() => {
    const q = search.trim().toLowerCase();
    return units.filter((u) => {
      if (propertyFilter && String(u.property_id) !== String(propertyFilter)) return false;
      if (!q) return true;

      const p = propMap.get(String(u.property_id));
      const hay = [
        unitName(u),
        String(u.id),
        propertyName(p),
        String(u.property_id ?? ""),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return hay.includes(q);
    });
  }, [units, propertyFilter, search, propMap]);

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Units</h2>
        <button
          onClick={startAdd}
          style={{ marginLeft: "auto", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          + Add Unit
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 12, marginBottom: 12 }}>
        <Select label="Property" value={propertyFilter} onChange={setPropertyFilter} options={propertyOptions} />
        <Field label="Search" value={search} onChange={setSearch} placeholder="Unit number, property name…" />
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
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Unit</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Property</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Beds</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Baths</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Sq Ft</th>
                <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUnits.map((u) => {
                const p = propMap.get(String(u.property_id));
                return (
                  <tr key={u.id}>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.unit_number || u.id}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p ? propertyName(p) : `#${u.property_id}`}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.bedrooms ?? "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.bathrooms ?? "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{u.sq_ft ?? u.sqft ?? "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2", textAlign: "right" }}>
                      <button
                        onClick={() => startEdit(u)}
                        style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", marginRight: 8 }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => remove(u)}
                        style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #f1b3b3", background: "#fff5f5", cursor: "pointer" }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filteredUnits.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: 14, opacity: 0.7 }}>
                    No units match this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

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
              <h3 style={{ margin: 0 }}>{editing ? "Edit Unit" : "Add Unit"}</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setOpen(false)} disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit" disabled={saving || !form.property_id || !form.unit_number}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <Select label="Property" value={form.property_id} onChange={(v) => setForm({ ...form, property_id: v })} options={propertyOptions} allLabel="Select…" />
            <Field label="Unit number" value={form.unit_number} onChange={(v) => setForm({ ...form, unit_number: v })} placeholder="e.g., 1A" />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <Field label="Bedrooms" type="number" value={form.bedrooms} onChange={(v) => setForm({ ...form, bedrooms: v })} />
              <Field label="Bathrooms" type="number" value={form.bathrooms} onChange={(v) => setForm({ ...form, bathrooms: v })} />
              <Field label="Sq Ft" type="number" value={form.sq_ft} onChange={(v) => setForm({ ...form, sq_ft: v })} />
            </div>
            <Field label="Notes" value={form.notes} onChange={(v) => setForm({ ...form, notes: v })} placeholder="optional" />
          </form>
        </div>
      )}
    </div>
  );
}
