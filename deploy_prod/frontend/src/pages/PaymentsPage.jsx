import React, { useEffect, useMemo, useState } from "react";
import { unwrapList } from "../utils/unwrapList";
import { leaseLabel, tenantName, unitLabel, propertyName, unitName } from "../utils/labels";

const API = import.meta.env.VITE_API_URL || "/api";

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
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
        <option value="">All</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [leases, setLeases] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [units, setUnits] = useState([]);
  const [properties, setProperties] = useState([]);

  const [month, setMonth] = useState(""); // YYYY-MM
  const [propertyId, setPropertyId] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [leaseId, setLeaseId] = useState("");

  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    lease_id: "",
    amount: "",
    payment_date: todayISO(),
    method: "manual",
    notes: "",
  });

  const propMap = useMemo(() => new Map(properties.map((p) => [String(p.id), p])), [properties]);
  const unitMap = useMemo(() => new Map(units.map((u) => [String(u.id), u])), [units]);
  const tenantMap = useMemo(() => new Map(tenants.map((t) => [String(t.id), t])), [tenants]);
  const leaseMap = useMemo(() => new Map(leases.map((l) => [String(l.id), l])), [leases]);

  async function loadAll() {
    setLoading(true);
    setErr("");
    try {
      const q = month ? `?month=${encodeURIComponent(month)}` : "";
      const [pR, lR, tR, uR, prR] = await Promise.all([
        fetch(`${API}/payments${q}`),
        fetch(`${API}/leases`),
        fetch(`${API}/tenants`),
        fetch(`${API}/units`),
        fetch(`${API}/properties`),
      ]);

      setPayments(unwrapList(await pR.json()));
      setLeases(unwrapList(await lR.json()));
      setTenants(unwrapList(await tR.json()));
      setUnits(unwrapList(await uR.json()));
      setProperties(unwrapList(await prR.json()));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, [month]);

  const propertyOptions = useMemo(
    () => properties.map((p) => ({ value: String(p.id), label: propertyName(p) })),
    [properties]
  );

  const tenantOptions = useMemo(
    () => tenants.map((t) => ({ value: String(t.id), label: tenantName(t) })),
    [tenants]
  );

  const leaseOptions = useMemo(() => {
    return leases.map((l) => ({
      value: String(l.id),
      label: leaseLabel(l, unitMap, tenantMap, propMap),
    }));
  }, [leases, unitMap, tenantMap, propMap]);

  const filteredPayments = useMemo(() => {
    let rows = payments;

    if (leaseId) {
      rows = rows.filter((p) => String(p.lease_id) === String(leaseId));
    }

    if (tenantId || propertyId) {
      rows = rows.filter((p) => {
        const l = leaseMap.get(String(p.lease_id));
        if (!l) return false;

        if (tenantId && String(l.tenant_id) !== String(tenantId)) return false;

        if (propertyId) {
          const u = unitMap.get(String(l.unit_id));
          if (!u) return false;
          if (String(u.property_id) !== String(propertyId)) return false;
        }

        return true;
      });
    }

    return rows;
  }, [payments, leaseId, tenantId, propertyId, leaseMap, unitMap]);

  function exportCsv() {
    const filename = month ? `payments_${month}.csv` : `payments.csv`;
    const rows = [
      ["payment_id","payment_date","amount","method","notes","lease_id","property","unit","tenant"],
      ...filteredPayments.map((p) => {
        const l = leaseMap.get(String(p.lease_id));
        const u = l ? unitMap.get(String(l.unit_id)) : null;
        const pr = u ? propMap.get(String(u.property_id)) : null;
        const t = l ? tenantMap.get(String(l.tenant_id)) : null;

        return [
          p.id,
          p.payment_date,
          p.amount,
          p.method,
          p.notes,
          p.lease_id,
          propertyName(pr),
          unitName(u),
          tenantName(t),
        ];
      }),
    ];
    downloadCsv(filename, rows);
  }

  function startAdd() {
    setForm({ lease_id: "", amount: "", payment_date: todayISO(), method: "manual", notes: month ? `Rent ${month}` : "" });
    setOpen(true);
  }

  async function save(e) {
    e?.preventDefault?.();
    setSaving(true);
    setErr("");
    try {
      const payload = {
        lease_id: numOrNull(form.lease_id),
        amount: numOrNull(form.amount),
        payment_date: form.payment_date || todayISO(),
        method: form.method || "manual",
        notes: form.notes?.trim() || null,
      };

      const r = await fetch(`${API}/payments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`POST failed: ${r.status} ${await r.text()}`);
      setOpen(false);
      await loadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Payments</h2>

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
          onClick={exportCsv}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Export CSV
        </button>

        <button
          onClick={startAdd}
          style={{ marginLeft: "auto", padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          + Record Payment
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 2fr", gap: 12, marginBottom: 12 }}>
        <Select label="Property" value={propertyId} onChange={setPropertyId} options={propertyOptions} />
        <Select label="Tenant" value={tenantId} onChange={setTenantId} options={tenantOptions} />
        <Select label="Lease" value={leaseId} onChange={setLeaseId} options={leaseOptions} />
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
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Date</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Amount</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Method</th>
                <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Lease</th>
              </tr>
            </thead>
            <tbody>
              {filteredPayments.map((p) => {
                const l = leaseMap.get(String(p.lease_id));
                return (
                  <tr key={p.id}>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.payment_date || "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.amount ?? "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{p.method || "-"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>
                      {l ? leaseLabel(l, unitMap, tenantMap, propMap) : `Lease #${p.lease_id}`}
                    </td>
                  </tr>
                );
              })}
              {filteredPayments.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ padding: 14, opacity: 0.7 }}>
                    No payments for this filter.
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
            style={{ width: "min(860px, 100%)", background: "white", borderRadius: 14, padding: 16, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>Record Payment</h3>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <button type="button" onClick={() => setOpen(false)} disabled={saving}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
                  Cancel
                </button>
                <button type="submit" disabled={saving || !form.lease_id || !form.amount}
                  style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}>
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </div>

            <Select label="Lease" value={form.lease_id} onChange={(v) => setForm({ ...form, lease_id: v })} options={leaseOptions} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <Field label="Amount" type="number" value={form.amount} onChange={(v) => setForm({ ...form, amount: v })} />
              <Field label="Payment date" type="date" value={form.payment_date} onChange={(v) => setForm({ ...form, payment_date: v })} />
              <Field label="Method" value={form.method} onChange={(v) => setForm({ ...form, method: v })} placeholder="manual / venmo / etc." />
            </div>
            <Field label="Notes" value={form.notes} onChange={(v) => setForm({ ...form, notes: v })} placeholder={month ? `Rent ${month}` : ""} />
          </form>
        </div>
      )}
    </div>
  );
}
