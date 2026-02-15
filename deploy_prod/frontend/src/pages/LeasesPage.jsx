import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { unwrapList } from "../utils/unwrapList";
import { tenantName as tn, propertyName as pn, unitName as un } from "../utils/labels";

const API = import.meta.env.VITE_API_URL || "/api";

function yyyymmToday() {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  return `${d.getFullYear()}-${mm}`;
}
function yyyyMMddToday() {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}
function money(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "-";
  return v.toLocaleString(undefined, { style: "currency", currency: "USD" });
}
function numOrNull(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}
function csvEscape(x) {
  if (x === null || x === undefined) return "";
  const s = String(x);
  if (s.includes('"') || s.includes(",") || s.includes("\n")) return `"${s.replaceAll('"', '""')}"`;
  return s;
}
function downloadCsv(filename, rows) {
  const csv = rows.map(r => r.map(csvEscape).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
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

function Select({ label, value, onChange, options }) {
  return (
    <label style={{ display: "block", marginBottom: 10 }}>
      <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>{label}</div>
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", outline: "none", background: "white" }}
      >
        <option value="">Select…</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function LeasesPage() {
  const loc = useLocation();
  const nav = useNavigate();

  const [leases, setLeases] = useState([]);
  const [units, setUnits] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [properties, setProperties] = useState([]);
  const [payments, setPayments] = useState([]);

  const [month, setMonth] = useState(yyyymmToday());
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  // Lease modal
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    unit_id: "",
    tenant_id: "",
    monthly_rent: "",
    start_date: "",
    end_date: "",
    security_deposit: "",
  });

  // Payment modal (single)
  const [payOpen, setPayOpen] = useState(false);
  const [paySaving, setPaySaving] = useState(false);
  const [payForm, setPayForm] = useState({
    lease_id: "",
    amount: "",
    payment_date: yyyyMMddToday(),
    method: "manual",
    notes: "",
  });

  // Drawer
  const [drawerLeaseId, setDrawerLeaseId] = useState(null);

  // Bulk modal
  const [bulkOpen, setBulkOpen] = useState(false);
  const [bulkSaving, setBulkSaving] = useState(false);
  const [bulkSelected, setBulkSelected] = useState({}); // leaseId -> bool
  const [bulkResult, setBulkResult] = useState(null); // {ok, fail}

  const propMap = useMemo(() => new Map(properties.map((p) => [String(p.id), p])), [properties]);
  const unitMap = useMemo(() => new Map(units.map((u) => [String(u.id), u])), [units]);
  const tenantMap = useMemo(() => new Map(tenants.map((t) => [String(t.id), t])), [tenants]);

  // URL support: /leases?new=1 and /leases?month=YYYY-MM
  useEffect(() => {
    const qs = new URLSearchParams(loc.search);
    const m = qs.get("month");
    if (m && m !== month) setMonth(m);
    if (qs.get("new") === "1") {
      startAddLease();
      nav(loc.pathname, { replace: true });
    }
  }, [loc.search]);

  const paidByLeaseId = useMemo(() => {
    const m = new Map();
    for (const p of payments) {
      const key = String(p.lease_id);
      const amt = Number(p.amount) || 0;
      m.set(key, (m.get(key) || 0) + amt);
    }
    return m;
  }, [payments]);

  function tenantName(t) {
    return tn(t) || "-";
  }

  function unitLabel(u) {
    if (!u) return "";
    const p = propMap.get(String(u.property_id));
    return `${pn(p) || `Property #${u.property_id}`} — ${un(u) || `Unit #${u.id}`}`;
  }

  const unitOptions = units.map((u) => ({ value: String(u.id), label: unitLabel(u) }));
  const tenantOptions = tenants.map((t) => ({ value: String(t.id), label: tenantName(t) }));

  async function loadAll() {
    setLoading(true);
    setErr("");
    try {
      const [lR, uR, tR, pR, payR] = await Promise.all([
        fetch(`${API}/leases`),
        fetch(`${API}/units`),
        fetch(`${API}/tenants`),
        fetch(`${API}/properties`),
        fetch(`${API}/payments?month=${encodeURIComponent(month)}`),
      ]);

      setLeases(unwrapList(await lR.json()));
      setUnits(unwrapList(await uR.json()));
      setTenants(unwrapList(await tR.json()));
      setProperties(unwrapList(await pR.json()));
      setPayments(unwrapList(await payR.json()));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, [month]);

  function statusForLease(l) {
    const due = Number(l.monthly_rent) || 0;
    const paid = paidByLeaseId.get(String(l.id)) || 0;
    const outstanding = Math.max(0, due - paid);
    let status = "Unpaid";
    if (paid >= due && due > 0) status = "Paid";
    else if (paid > 0) status = "Partial";
    return { due, paid, outstanding, status };
  }

  const delinquent = useMemo(() => {
    return leases
      .map((l) => ({ l, s: statusForLease(l) }))
      .filter((x) => x.s.outstanding > 0)
      .sort((a, b) => b.s.outstanding - a.s.outstanding);
  }, [leases, paidByLeaseId]);

  function startAddLease() {
    setEditing(null);
    setForm({ unit_id: "", tenant_id: "", monthly_rent: "", start_date: "", end_date: "", security_deposit: "" });
    setOpen(true);
  }

  function startEditLease(l) {
    setEditing(l);
    setForm({
      unit_id: l?.unit_id != null ? String(l.unit_id) : "",
      tenant_id: l?.tenant_id != null ? String(l.tenant_id) : "",
      monthly_rent: l?.monthly_rent ?? "",
      start_date: l?.start_date ?? "",
      end_date: l?.end_date ?? "",
      security_deposit: l?.security_deposit ?? "",
    });
    setOpen(true);
  }

  async function saveLease(e) {
    e?.preventDefault?.();
    setSaving(true);
    setErr("");

    const isEdit = Boolean(editing?.id);
    const url = isEdit ? `${API}/leases/${editing.id}` : `${API}/leases`;
    const method = isEdit ? "PUT" : "POST";

    try {
      const payload = {
        unit_id: numOrNull(form.unit_id),
        tenant_id: numOrNull(form.tenant_id),
        monthly_rent: numOrNull(form.monthly_rent),
        start_date: form.start_date || null,
        end_date: form.end_date || null,
        security_deposit: numOrNull(form.security_deposit),
      };

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

  async function deleteLease(l) {
    if (!l?.id) return;
    if (!confirm(`Delete lease #${l.id}?`)) return;

    setErr("");
    try {
      const r = await fetch(`${API}/leases/${l.id}`, { method: "DELETE" });
      if (!r.ok) throw new Error(`DELETE failed: ${r.status} ${await r.text()}`);
      await loadAll();
    } catch (e) {
      setErr(String(e));
    }
  }

  function openDrawer(l) {
    setDrawerLeaseId(String(l.id));
  }

  function startPaymentForLease(l) {
    const { due, outstanding } = statusForLease(l);
    const suggested = outstanding > 0 ? outstanding : due;

    setPayForm({
      lease_id: String(l.id),
      amount: String(suggested || ""),
      payment_date: yyyyMMddToday(),
      method: "manual",
      notes: month ? `Rent ${month}` : "",
    });
    setPayOpen(true);
  }

  async function savePayment(e) {
    e?.preventDefault?.();
    setPaySaving(true);
    setErr("");

    try {
      const payload = {
        lease_id: numOrNull(payForm.lease_id),
        amount: numOrNull(payForm.amount),
        payment_date: payForm.payment_date || yyyyMMddToday(),
        method: payForm.method || "manual",
        notes: payForm.notes?.trim() || null,
      };

      const r = await fetch(`${API}/payments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!r.ok) throw new Error(`POST /payments failed: ${r.status} ${await r.text()}`);
      setPayOpen(false);
      await loadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setPaySaving(false);
    }
  }

  function exportRentRoll() {
    const filename = `rent_roll_${month}.csv`;
    const rows = [
      ["lease_id","property","unit","tenant","monthly_rent","paid","outstanding","status","start_date","end_date","unit_id","tenant_id"],
      ...leases.map((l) => {
        const u = unitMap.get(String(l.unit_id));
        const p = u ? propMap.get(String(u.property_id)) : null;
        const t = tenantMap.get(String(l.tenant_id));
        const s = statusForLease(l);
        return [
          l.id,
          p ? pn(p) : (u ? `Property #${u.property_id}` : ""),
          u ? (u.unit_number || u.id) : "",
          tenantName(t),
          l.monthly_rent,
          s.paid,
          s.outstanding,
          s.status,
          l.start_date || "",
          l.end_date || "",
          l.unit_id,
          l.tenant_id,
        ];
      }),
    ];
    downloadCsv(filename, rows);
  }

  function openBulk() {
    const init = {};
    delinquent.forEach(({ l }) => { init[String(l.id)] = true; });
    setBulkSelected(init);
    setBulkResult(null);
    setBulkOpen(true);
  }

  async function runBulk(e) {
    e?.preventDefault?.();
    setBulkSaving(true);
    setErr("");
    setBulkResult(null);

    const selected = delinquent.filter(({ l }) => bulkSelected[String(l.id)]);
    const ok = [];
    const fail = [];

    try {
      for (const { l, s } of selected) {
        const payload = {
          lease_id: Number(l.id),
          amount: Number(s.outstanding),
          payment_date: yyyyMMddToday(),
          method: "manual",
          notes: `Rent ${month} (bulk)`,
        };

        const r = await fetch(`${API}/payments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!r.ok) {
          const t = await r.text();
          fail.push({ lease_id: l.id, error: `${r.status} ${t}` });
        } else {
          ok.push(l.id);
        }
      }
      setBulkResult({ ok, fail });
      await loadAll();
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setBulkSaving(false);
    }
  }

  const drawerLease = drawerLeaseId ? leases.find((l) => String(l.id) === String(drawerLeaseId)) : null;
  const drawerUnit = drawerLease ? unitMap.get(String(drawerLease.unit_id)) : null;
  const drawerTenant = drawerLease ? tenantMap.get(String(drawerLease.tenant_id)) : null;
  const drawerStatus = drawerLease ? statusForLease(drawerLease) : null;
  const drawerPayments = drawerLease ? payments.filter((p) => String(p.lease_id) === String(drawerLease.id)) : [];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Leases</h2>

        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 12, opacity: 0.8 }}>Month</span>
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd" }}
          />
        </label>

        <button
          onClick={exportRentRoll}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Export Rent Roll CSV
        </button>

        <button
          onClick={openBulk}
          disabled={delinquent.length === 0}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: delinquent.length ? "#111" : "#f2f2f2", color: delinquent.length ? "white" : "#999", cursor: delinquent.length ? "pointer" : "not-allowed" }}
          title="Create payments for outstanding balances"
        >
          Bulk mark paid
        </button>

        <button
          onClick={startAddLease}
          style={{ marginLeft: "auto", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          + Add Lease
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
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Unit</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Tenant</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Due</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Paid</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Outstanding</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Status</th>
                <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leases.map((l) => {
                const u = unitMap.get(String(l.unit_id));
                const t = tenantMap.get(String(l.tenant_id));
                const s = statusForLease(l);

                return (
                  <tr key={l.id} onClick={() => openDrawer(l)} style={{ cursor: "pointer" }}>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{unitLabel(u)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{tenantName(t)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(s.due)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(s.paid)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(s.outstanding)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{s.status}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2", textAlign: "right" }}>
                      <button
                        onClick={(e) => { e.stopPropagation(); startPaymentForLease(l); }}
                        style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer", marginRight: 8 }}
                      >
                        Record payment
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); startEditLease(l); }}
                        style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer", marginRight: 8 }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteLease(l); }}
                        style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #f1b3b3", background: "#fff5f5", cursor: "pointer" }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
              {leases.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: 14, opacity: 0.7 }}>
                    No leases yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Drawer */}
      {drawerLease && (
        <div
          style={{
            position: "fixed",
            top: 0,
            right: 0,
            height: "100%",
            width: "min(520px, 92vw)",
            background: "white",
            borderLeft: "1px solid #eee",
            boxShadow: "0 10px 30px rgba(0,0,0,0.12)",
            padding: 16,
            overflow: "auto",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <div>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Lease #{drawerLease.id}</div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{unitLabel(drawerUnit)}</div>
              <div style={{ opacity: 0.85, marginTop: 4 }}>{tenantName(drawerTenant)}</div>
            </div>
            <button
              onClick={() => setDrawerLeaseId(null)}
              style={{ marginLeft: "auto", padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
            >
              Close
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 12 }}>
            <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 10 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Due</div>
              <div style={{ fontWeight: 700 }}>{money(drawerStatus?.due)}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 10 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Paid</div>
              <div style={{ fontWeight: 700 }}>{money(drawerStatus?.paid)}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 10 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Outstanding</div>
              <div style={{ fontWeight: 700 }}>{money(drawerStatus?.outstanding)}</div>
            </div>
          </div>

          <button
            onClick={() => startPaymentForLease(drawerLease)}
            style={{ width: "100%", padding: "10px 12px", borderRadius: 12, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer", marginBottom: 12 }}
          >
            Record payment for {month}
          </button>

          <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 8 }}>Payments for {month}</div>
          <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#fafafa" }}>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Date</th>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Amount</th>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Method</th>
                </tr>
              </thead>
              <tbody>
                {drawerPayments.map((p) => (
                  <tr key={p.id}>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.payment_date || "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(p.amount)}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.method || "-"}</td>
                  </tr>
                ))}
                {drawerPayments.length === 0 && (
                  <tr>
                    <td colSpan={3} style={{ padding: 12, opacity: 0.7 }}>No payments for this lease in {month}.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Lease modal */}
      {open && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}
          onClick={() => !saving && setOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={saveLease}
            style={{ width: "min(860px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>{editing ? "Edit Lease" : "Add Lease"}</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setOpen(false)} disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit" disabled={saving || !form.unit_id || !form.monthly_rent}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Select label="Unit" value={form.unit_id} onChange={(v) => setForm({ ...form, unit_id: v })} options={unitOptions} />
              <Select label="Tenant" value={form.tenant_id} onChange={(v) => setForm({ ...form, tenant_id: v })} options={tenantOptions} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <Field label="Monthly rent" type="number" value={form.monthly_rent} onChange={(v) => setForm({ ...form, monthly_rent: v })} />
              <Field label="Security deposit" type="number" value={form.security_deposit} onChange={(v) => setForm({ ...form, security_deposit: v })} />
              <div />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Start date" type="date" value={form.start_date} onChange={(v) => setForm({ ...form, start_date: v })} />
              <Field label="End date" type="date" value={form.end_date} onChange={(v) => setForm({ ...form, end_date: v })} />
            </div>
          </form>
        </div>
      )}

      {/* Payment modal */}
      {payOpen && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}
          onClick={() => !paySaving && setPayOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={savePayment}
            style={{ width: "min(860px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>Record Payment</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setPayOpen(false)} disabled={paySaving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit" disabled={paySaving || !payForm.lease_id || !payForm.amount}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {paySaving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <Field label="Lease ID" value={payForm.lease_id} onChange={(v) => setPayForm({ ...payForm, lease_id: v })} />
              <Field label="Amount" type="number" value={payForm.amount} onChange={(v) => setPayForm({ ...payForm, amount: v })} />
              <Field label="Payment date" type="date" value={payForm.payment_date} onChange={(v) => setPayForm({ ...payForm, payment_date: v })} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <Field label="Method" value={payForm.method} onChange={(v) => setPayForm({ ...payForm, method: v })} placeholder="manual / venmo / etc." />
              <Field label="Notes" value={payForm.notes} onChange={(v) => setPayForm({ ...payForm, notes: v })} placeholder={`Rent ${month}`} />
            </div>
          </form>
        </div>
      )}

      {/* Bulk modal */}
      {bulkOpen && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.35)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}
          onClick={() => !bulkSaving && setBulkOpen(false)}
        >
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={runBulk}
            style={{ width: "min(980px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>Bulk mark paid — {month}</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setBulkOpen(false)} disabled={bulkSaving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Close
                </button>
                <button type="submit" disabled={bulkSaving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {bulkSaving ? "Working…" : "Create payments"}
                </button>
              </div>
            </div>

            <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 10 }}>
              Creates one payment per selected lease for its outstanding balance.
            </div>

            <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden", maxHeight: "50vh", overflowY: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#fafafa" }}>
                    <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Select</th>
                    <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Lease</th>
                    <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Outstanding</th>
                  </tr>
                </thead>
                <tbody>
                  {delinquent.map(({ l, s }) => {
                    const u = unitMap.get(String(l.unit_id));
                    const t = tenantMap.get(String(l.tenant_id));
                    return (
                      <tr key={l.id}>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>
                          <input
                            type="checkbox"
                            checked={!!bulkSelected[String(l.id)]}
                            onChange={(e) => setBulkSelected({ ...bulkSelected, [String(l.id)]: e.target.checked })}
                          />
                        </td>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>
                          Lease #{l.id} — {unitLabel(u)} — {tenantName(t)}
                        </td>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(s.outstanding)}</td>
                      </tr>
                    );
                  })}
                  {delinquent.length === 0 && (
                    <tr><td colSpan={3} style={{ padding: 12, opacity: 0.7 }}>No outstanding balances for {month}.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {bulkResult && (
              <div style={{ marginTop: 12, border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Result</div>
                <div>Success: {bulkResult.ok.length}</div>
                <div>Failed: {bulkResult.fail.length}</div>
                {bulkResult.fail.length > 0 && (
                  <div style={{ marginTop: 8, fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap" }}>
                    {bulkResult.fail.map(f => `lease ${f.lease_id}: ${f.error}`).join("\n")}
                  </div>
                )}
              </div>
            )}
          </form>
        </div>
      )}
    </div>
  );
}
