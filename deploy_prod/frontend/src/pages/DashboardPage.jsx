import React, { useEffect, useMemo, useState } from "react";
import { unwrapList } from "../utils/unwrapList";
import { tenantName, propertyName, unitName } from "../utils/labels";
import { money, yyyymmToday } from "../utils/api";

const API = import.meta.env.VITE_API_URL || "/api";

export default function DashboardPage() {
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  const [leases, setLeases] = useState([]);
  const [units, setUnits] = useState([]);
  const [properties, setProperties] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [payments, setPayments] = useState([]);

  const month = yyyymmToday();

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const [lR, uR, prR, tR, payR] = await Promise.all([
        fetch(`${API}/leases`),
        fetch(`${API}/units`),
        fetch(`${API}/properties`),
        fetch(`${API}/tenants`),
        fetch(`${API}/payments?month=${encodeURIComponent(month)}`),
      ]);

      setLeases(unwrapList(await lR.json()));
      setUnits(unwrapList(await uR.json()));
      setProperties(unwrapList(await prR.json()));
      setTenants(unwrapList(await tR.json()));
      setPayments(unwrapList(await payR.json()));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  const propMap = useMemo(() => new Map(properties.map((p) => [String(p.id), p])), [properties]);
  const unitMap = useMemo(() => new Map(units.map((u) => [String(u.id), u])), [units]);
  const tenantMap = useMemo(() => new Map(tenants.map((t) => [String(t.id), t])), [tenants]);

  const paidByLeaseId = useMemo(() => {
    const m = new Map();
    for (const p of payments) {
      const key = String(p.lease_id);
      m.set(key, (m.get(key) || 0) + (Number(p.amount) || 0));
    }
    return m;
  }, [payments]);

  const delinquent = useMemo(() => {
    const rows = leases.map((l) => {
      const due = Number(l.monthly_rent) || 0;
      const paid = paidByLeaseId.get(String(l.id)) || 0;
      const outstanding = Math.max(0, due - paid);
      const u = unitMap.get(String(l.unit_id));
      const pr = u ? propMap.get(String(u.property_id)) : null;
      const t = tenantMap.get(String(l.tenant_id));
      return {
        lease_id: l.id,
        property: propertyName(pr) || (u ? `Property #${u.property_id}` : "-"),
        unit: unitName(u) || (u ? `Unit #${u.id}` : "-"),
        tenant: tenantName(t) || "-",
        due,
        paid,
        outstanding,
      };
    });

    return rows.filter(r => r.outstanding > 0).sort((a,b) => b.outstanding - a.outstanding);
  }, [leases, paidByLeaseId, unitMap, propMap, tenantMap]);

  const dueTotal = useMemo(() => leases.reduce((s,l) => s + (Number(l.monthly_rent) || 0), 0), [leases]);
  const paidTotal = useMemo(() => payments.reduce((s,p) => s + (Number(p.amount) || 0), 0), [payments]);
  const outTotal = Math.max(0, dueTotal - paidTotal);

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Dashboard</h2>

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
              <div style={{ fontSize: 12, opacity: 0.7 }}>Month</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{month}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Collected</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(paidTotal)}</div>
            </div>
            <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>Outstanding</div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{money(outTotal)}</div>
            </div>
          </div>

          <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
            <div style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
              <div style={{ fontSize: 14, fontWeight: 700 }}>Delinquent leases</div>
              <a
                href={`/leases?month=${encodeURIComponent(month)}`}
                style={{ marginLeft: "auto", fontSize: 12, textDecoration: "none" }}
              >
                Open Leases →
              </a>
            </div>

            {delinquent.length === 0 ? (
              <div style={{ opacity: 0.7 }}>No delinquent leases for {month}.</div>
            ) : (
              <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: "#fafafa" }}>
                      <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Property</th>
                      <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Unit</th>
                      <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Tenant</th>
                      <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>Outstanding</th>
                    </tr>
                  </thead>
                  <tbody>
                    {delinquent.slice(0, 10).map((r) => (
                      <tr key={r.lease_id}>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{r.property}</td>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{r.unit}</td>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{r.tenant}</td>
                        <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{money(r.outstanding)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
