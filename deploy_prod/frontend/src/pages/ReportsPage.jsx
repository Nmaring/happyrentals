import React, { useEffect, useMemo, useState } from "react";
import { unwrapList } from "../utils/unwrapList";
import { tenantName, propertyName, unitName } from "../utils/labels";

const API = import.meta.env.VITE_API_URL || "/api";

function yyyymmToday() {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  return `${d.getFullYear()}-${mm}`;
}
function money(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "-";
  return v.toLocaleString(undefined, { style: "currency", currency: "USD" });
}
function csvEscape(x) {
  if (x === null || x === undefined) return "";
  const s = String(x);
  if (s.includes('"') || s.includes(",") || s.includes("\n")) return `"${s.replaceAll('"', '""')}"`;
  return s;
}
function downloadCsv(filename, rows) {
  const csv = rows.map((r) => r.map(csvEscape).join(",")).join("\n");
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

export default function ReportsPage() {
  const [month, setMonth] = useState(yyyymmToday());
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [dbInfo, setDbInfo] = useState(null);

  const [payments, setPayments] = useState([]);
  const [leases, setLeases] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [units, setUnits] = useState([]);
  const [properties, setProperties] = useState([]);

  const propMap = useMemo(() => new Map(properties.map((p) => [String(p.id), p])), [properties]);
  const unitMap = useMemo(() => new Map(units.map((u) => [String(u.id), u])), [units]);
  const tenantMap = useMemo(() => new Map(tenants.map((t) => [String(t.id), t])), [tenants]);
  const leaseMap = useMemo(() => new Map(leases.map((l) => [String(l.id), l])), [leases]);

  const paidByLeaseId = useMemo(() => {
    const m = new Map();
    for (const p of payments) {
      const key = String(p.lease_id);
      m.set(key, (m.get(key) || 0) + (Number(p.amount) || 0));
    }
    return m;
  }, [payments]);

  function leaseStatus(l) {
    const due = Number(l.monthly_rent) || 0;
    const paid = paidByLeaseId.get(String(l.id)) || 0;
    const outstanding = Math.max(0, due - paid);
    let status = "Unpaid";
    if (paid >= due && due > 0) status = "Paid";
    else if (paid > 0) status = "Partial";
    return { due, paid, outstanding, status };
  }

  async function loadAll() {
    setLoading(true);
    setErr("");
    try {
      const q = `?month=${encodeURIComponent(month)}`;
      const [dbR, payR, leaseR, tenantR, unitR, propR] = await Promise.all([
        fetch(`${API}/admin/db`),
        fetch(`${API}/payments${q}`),
        fetch(`${API}/leases`),
        fetch(`${API}/tenants`),
        fetch(`${API}/units`),
        fetch(`${API}/properties`),
      ]);

      setDbInfo(await dbR.json());
      setPayments(unwrapList(await payR.json()));
      setLeases(unwrapList(await leaseR.json()));
      setTenants(unwrapList(await tenantR.json()));
      setUnits(unwrapList(await unitR.json()));
      setProperties(unwrapList(await propR.json()));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, [month]);

  const totals = useMemo(() => {
    const due = leases.reduce((s, l) => s + (Number(l.monthly_rent) || 0), 0);
    const collected = payments.reduce((s, p) => s + (Number(p.amount) || 0), 0);
    const outstanding = Math.max(0, due - collected);
    return { due, collected, outstanding };
  }, [leases, payments]);

  function exportPaymentsCsv() {
    const rows = [
      ["payment_id","payment_date","amount","method","notes","lease_id","property","unit","tenant"],
      ...payments.map((p) => {
        const l = leaseMap.get(String(p.lease_id));
        const u = l ? unitMap.get(String(l.unit_id)) : null;
        const pr = u ? propMap.get(String(u.property_id)) : null;
        const t = l ? tenantMap.get(String(l.tenant_id)) : null;

        return [
          p.id, p.payment_date, p.amount, p.method, p.notes, p.lease_id,
          propertyName(pr),
          u ? (u.unit_number || u.id) : "",
          tenantName(t),
        ];
      }),
    ];
    downloadCsv(`payments_${month}.csv`, rows);
  }

  function exportRentRollCsv(onlyDelinquent = false) {
    const rows = [
      ["lease_id","property","unit","tenant","monthly_rent","paid","outstanding","status","start_date","end_date","unit_id","tenant_id"],
      ...leases
        .map((l) => {
          const u = unitMap.get(String(l.unit_id));
          const pr = u ? propMap.get(String(u.property_id)) : null;
          const t = tenantMap.get(String(l.tenant_id));
          const s = leaseStatus(l);

          return {
            lease_id: l.id,
            property: pr ? propertyName(pr) : (u ? `Property #${u.property_id}` : ""),
            unit: u ? (u.unit_number || u.id) : "",
            tenant: tenantName(t),
            monthly_rent: l.monthly_rent,
            paid: s.paid,
            outstanding: s.outstanding,
            status: s.status,
            start_date: l.start_date || "",
            end_date: l.end_date || "",
            unit_id: l.unit_id,
            tenant_id: l.tenant_id,
          };
        })
        .filter((r) => (onlyDelinquent ? Number(r.outstanding) > 0 : true))
        .map((r) => [
          r.lease_id, r.property, r.unit, r.tenant,
          r.monthly_rent, r.paid, r.outstanding, r.status,
          r.start_date, r.end_date, r.unit_id, r.tenant_id,
        ]),
    ];

    const name = onlyDelinquent ? `delinquent_${month}.csv` : `rent_roll_${month}.csv`;
    downloadCsv(name, rows);
  }

  function downloadBackup() {
    window.location.href = `${API}/admin/backup`;
  }

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Reports</h2>

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
          onClick={downloadBackup}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Download DB backup
        </button>

        <button
          onClick={loadAll}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Refresh
        </button>
      </div>

      {dbInfo && (
        <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 10 }}>
          DB: {dbInfo.db_path} • exists: {String(dbInfo.exists)} • size: {dbInfo.size}
        </div>
      )}

      {err && (
        <div style={{ background: "#ffe9e9", border: "1px solid #ffb3b3", padding: 10, borderRadius: 10, marginBottom: 12 }}>
          {err}
        </div>
      )}

      {loading ? (
        <div>Loading…</div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12, marginBottom: 12 }}>
            <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Due</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(totals.due)}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Collected</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(totals.collected)}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Outstanding</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(totals.outstanding)}</div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
            <button onClick={exportPaymentsCsv} style={{ padding: 12, borderRadius: 14, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
              Export Payments CSV
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>{payments.length} rows</div>
            </button>

            <button onClick={() => exportRentRollCsv(false)} style={{ padding: 12, borderRadius: 14, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
              Export Rent Roll CSV
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>{leases.length} leases</div>
            </button>

            <button onClick={() => exportRentRollCsv(true)} style={{ padding: 12, borderRadius: 14, border: "1px solid #ddd", background: "white", cursor: "pointer" }}>
              Export Delinquent CSV
              <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>
                {leases.filter((l) => leaseStatus(l).outstanding > 0).length} delinquent
              </div>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
