import React from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
const API = import.meta.env.VITE_API_URL || "/api";

function unwrapList(x) {
  if (!x) return [];
  if (Array.isArray(x)) return x;
  if (x && Array.isArray(x.value)) return x.value; // sometimes backend returns { value: [...], Count: n }
  if (x && Array.isArray(x.items)) return x.items;
  if (x && Array.isArray(x.results)) return x.results;
  return [];
}

function Modal({ open, title, onClose, children }) {
  if (!open) return null;
  return (
    <div style={styles.overlay} onMouseDown={onClose}>
      <div style={styles.modal} onMouseDown={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <div style={{ fontWeight: 900 }}>{title}</div>
          <button type="button" onClick={onClose} style={styles.btnGhost}>✕</button>
        </div>
        <div style={styles.modalBody}>{children}</div>
      </div>
    </div>
  );
}

export default function LeasesPage() {
  const nav = useNavigate();

  const [searchParams] = useSearchParams();
  const qpUnitId = searchParams.get("unit_id") || "";
  const qpTenantId = searchParams.get("tenant_id") || "";


  const qpNew = searchParams.get("new") || "";



  const [leases, setLeases] = React.useState([]);
  const [units, setUnits] = React.useState([]);
  const [tenants, setTenants] = React.useState([]);

  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  const [open, setOpen] = React.useState(false);


  React.useEffect(() => {
    if (qpNew === "1") {
      // open modal prefilled from query params
      openCreate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [qpNew, qpUnitId, qpTenantId]);

  const emptyForm = {
    tenant_id: qpTenantId || "",
    unit_id: qpUnitId || "",
    start_date: "",
    end_date: "",
    lease_type: "month_to_month",
    monthly_rent: "",
    security_deposit: "",
    rent_due_day: "1",
    status: "active",
    notes: "",
  };

  const [form, setForm] = React.useState(emptyForm);

  const tenantLabelById = React.useMemo(() => {
    const m = {};
    (tenants || []).forEach((t) => {
      m[String(t.id)] = `${t.first_name || ""} ${t.last_name || ""}`.trim() || `Tenant ${t.id}`;
    });
    return m;
  }, [tenants]);

  const unitLabelById = React.useMemo(() => {
    const m = {};
    (units || []).forEach((u) => {
      m[String(u.id)] = u.label || u.unit_number || u.name || `Unit ${u.id}`;
    });
    return m;
  }, [units]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [uRes, tRes] = await Promise.all([
        fetch(`${API}/units`),
        fetch(`${API}/tenants`),
      ]);
      if (!uRes.ok) throw new Error(`GET /units failed (${uRes.status})`);
      if (!tRes.ok) throw new Error(`GET /tenants failed (${tRes.status})`);

      const uJson = await uRes.json();
      const tJson = await tRes.json();

      setUnits(unwrapList(uJson));
      setTenants(unwrapList(tJson));

      const qs = new URLSearchParams();
      if (qpUnitId) qs.set("unit_id", qpUnitId);
      if (qpTenantId) qs.set("tenant_id", qpTenantId);

      const url = qs.toString() ? `${API}/leases?${qs.toString()}` : `${API}/leases`;
      const lRes = await fetch(url);
      if (!lRes.ok) throw new Error(`GET /leases failed (${lRes.status})`);
      const lJson = await lRes.json();
      setLeases(unwrapList(lJson));
    } catch (e) {
      setError(String(e?.message || e));
      setLeases([]);
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => { load(); }, [qpUnitId, qpTenantId]);

  function onChange(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  function openCreate() {
    setError("");
    setForm({
      ...emptyForm,
      tenant_id: qpTenantId || emptyForm.tenant_id,
      unit_id: qpUnitId || emptyForm.unit_id,
    });
    setOpen(true);
  }

  async function createLease(e) {
    e.preventDefault();
    setError("");

    const payload = {
      tenant_id: Number(form.tenant_id),
      unit_id: Number(form.unit_id),
      start_date: String(form.start_date || "").trim(),
      end_date: form.lease_type === "fixed_term" ? (String(form.end_date || "").trim() || null) : null,
      lease_type: String(form.lease_type || "month_to_month"),
      monthly_rent: Number(form.monthly_rent),
      security_deposit: form.security_deposit === "" ? 0 : Number(form.security_deposit),
      rent_due_day: Number(form.rent_due_day || 1),
      status: String(form.status || "active"),
      notes: String(form.notes || ""),
    };

    if (!Number.isInteger(payload.tenant_id) || payload.tenant_id <= 0) {
      setError("Select a tenant.");
      return;
    }
    if (!Number.isInteger(payload.unit_id) || payload.unit_id <= 0) {
      setError("Select a unit.");
      return;
    }
    if (!payload.start_date) {
      setError("Start date is required.");
      return;
    }
    if (!Number.isFinite(payload.monthly_rent) || payload.monthly_rent <= 0) {
      setError("Monthly rent must be a number > 0.");
      return;
    }
    if (payload.lease_type === "fixed_term" && !payload.end_date) {
      setError("End date is required for fixed-term leases.");
      return;
    }

    try {
      const r = await fetch(`${API}/leases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) {
        const t = await r.text();
        throw new Error(`POST /leases failed (${r.status}): ${t}`);
      }
      setOpen(false);
      await load();
    } catch (e2) {
      setError(String(e2?.message || e2));
    }
  }

  async function deleteLease(id) {
    if (!confirm("Delete this lease?")) return;
    setError("");
    try {
      const r = await fetch(`${API}/leases/${id}`, { method: "DELETE" });
      if (!r.ok) {
        const t = await r.text();
        throw new Error(`DELETE /leases/${id} failed (${r.status}): ${t}`);
      }
      await load();
    } catch (e) {
      setError(String(e?.message || e));
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.headerRow}>
        <div>
          <div style={styles.h1}>Leases</div>
          <div style={styles.sub}>
            {qpUnitId ? `Filtered by unit ${qpUnitId}. ` : ""}
            {qpTenantId ? `Filtered by tenant ${qpTenantId}.` : ""}
          </div>
        </div>
        <button type="button" style={styles.btnPrimary} onClick={openCreate}>
          + New Lease
        </button>
      </div>

      {error ? <div style={styles.err}>{error}</div> : null}

      <div style={styles.card}>
        <div style={styles.tableHead}>
          <div style={{ fontWeight: 800 }}>Tenant</div>
          <div style={{ fontWeight: 800 }}>Unit</div>
          <div style={{ fontWeight: 800 }}>Dates</div>
          <div style={{ fontWeight: 800, textAlign: "right" }}>Rent</div>
          <div style={{ fontWeight: 800, textAlign: "right" }}>Actions</div>
        </div>

        {loading ? (
          <div style={{ padding: 14, opacity: 0.75 }}>Loading…</div>
        ) : leases.length === 0 ? (
          <div style={{ padding: 14, opacity: 0.75 }}>No leases found.</div>
        ) : (
          leases.map((l) => (
            <div key={l.id} style={styles.row}>
              <div>{tenantLabelById[String(l.tenant_id)] || `Tenant ${l.tenant_id}`}</div>
              <div>{unitLabelById[String(l.unit_id)] || `Unit ${l.unit_id}`}</div>
              <div style={{ opacity: 0.85 }}>
                {String(l.start_date || "")}
                {l.end_date ? ` → ${l.end_date}` : ""}
                {l.lease_type ? ` • ${l.lease_type}` : ""}
              </div>
              <div style={{ textAlign: "right" }}>${Number(l.monthly_rent || 0).toFixed(2)}</div>
              <div style={{ textAlign: "right" }}>
                <button type="button" style={styles.btnGhost} onClick={() => nav(`/payments?lease_id=${encodeURIComponent(String(l.id))}`)}>Payments</button>
                <button type="button" style={styles.btnGhost} onClick={() => nav(`/payments?lease_id=${encodeURIComponent(String(l.id))}&new=1`)}>New Payment</button>
                <button type="button" style={styles.btnGhost} onClick={() => window.location.href = `/payments?lease_id=${encodeURIComponent(String(l.id))}`}>Payments</button>
                <button type="button" style={styles.btnGhost} onClick={() => window.location.href = `/payments?lease_id=${encodeURIComponent(String(l.id))}&new=1`}>New Payment</button>
                <button type="button" style={styles.btnGhost} onClick={() => window.location.href = `/payments?lease_id=${encodeURIComponent(String(l.id))}`}>Payments</button>
                <button type="button" style={styles.btnGhost} onClick={() => window.location.href = `/payments?lease_id=${encodeURIComponent(String(l.id))}&new=1`}>New Payment</button>
                <button type="button" style={styles.btnGhost} onClick={() => deleteLease(l.id)}>Delete</button>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal open={open} title="Create Lease" onClose={() => setOpen(false)}>
        <form onSubmit={createLease} style={{ display: "grid", gap: 12 }}>
          <div style={styles.grid2}>
            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Tenant</div>
              <select style={styles.input} value={form.tenant_id} onChange={(e) => onChange("tenant_id", e.target.value)}>
                <option value="">Select…</option>
                {tenants.map((t) => (
                  <option key={t.id} value={String(t.id)}>
                    {(tenantLabelById[String(t.id)] || `Tenant ${t.id}`)}
                  </option>
                ))}
              </select>
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Unit</div>
              <select style={styles.input} value={form.unit_id} onChange={(e) => onChange("unit_id", e.target.value)}>
                <option value="">Select…</option>
                {units.map((u) => (
                  <option key={u.id} value={String(u.id)}>
                    {(unitLabelById[String(u.id)] || `Unit ${u.id}`)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={styles.grid2}>
            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Lease Type</div>
              <select style={styles.input} value={form.lease_type} onChange={(e) => onChange("lease_type", e.target.value)}>
                <option value="month_to_month">month_to_month</option>
                <option value="fixed_term">fixed_term</option>
                <option value="open_ended">open_ended</option>
              </select>
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Rent Due Day (1–28)</div>
              <input type="number" min="1" max="28" style={styles.input} value={form.rent_due_day} onChange={(e) => onChange("rent_due_day", e.target.value)} />
            </label>
          </div>

          <div style={styles.grid2}>
            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Start Date</div>
              <input type="date" style={styles.input} value={form.start_date} onChange={(e) => onChange("start_date", e.target.value)} />
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>End Date (fixed term only)</div>
              <input type="date" style={styles.input} value={form.end_date} disabled={form.lease_type !== "fixed_term"} onChange={(e) => onChange("end_date", e.target.value)} />
            </label>
          </div>

          <div style={styles.grid2}>
            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Monthly Rent</div>
              <input type="number" step="0.01" style={styles.input} value={form.monthly_rent} onChange={(e) => onChange("monthly_rent", e.target.value)} />
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <div style={styles.label}>Security Deposit</div>
              <input type="number" step="0.01" style={styles.input} value={form.security_deposit} onChange={(e) => onChange("security_deposit", e.target.value)} />
            </label>
          </div>

          <label style={{ display: "grid", gap: 6 }}>
            <div style={styles.label}>Notes</div>
            <textarea style={{ ...styles.input, minHeight: 80 }} value={form.notes} onChange={(e) => onChange("notes", e.target.value)} />
          </label>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
            <button type="button" style={styles.btn} onClick={() => setOpen(false)}>Cancel</button>
            <button type="submit" style={styles.btnPrimary}>Create</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

const styles = {
  page: { padding: 18, display: "grid", gap: 14 },
  headerRow: { display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 12 },
  h1: { fontSize: 26, fontWeight: 900, letterSpacing: -0.3 },
  sub: { color: "#475569", marginTop: 4 },

  err: { background: "#fff1f2", border: "1px solid #fecdd3", color: "#9f1239", padding: 10, borderRadius: 12 },

  card: { background: "white", border: "1px solid #e5e7eb", borderRadius: 16, overflow: "hidden" },
  tableHead: { display: "grid", gridTemplateColumns: "1.4fr 1.4fr 2fr 1fr 1fr", gap: 10, padding: 12, borderBottom: "1px solid #e5e7eb", background: "#fafafa" },
  row: { display: "grid", gridTemplateColumns: "1.4fr 1.4fr 2fr 1fr 1fr", gap: 10, padding: 12, borderBottom: "1px solid #f1f5f9", alignItems: "center" },

  btn: { padding: "10px 12px", borderRadius: 12, border: "1px solid #e5e7eb", background: "white", cursor: "pointer" },
  btnPrimary: { padding: "10px 12px", borderRadius: 12, border: "1px solid #1d4ed8", background: "#2563eb", color: "white", cursor: "pointer" },
  btnGhost: { padding: "8px 10px", borderRadius: 10, border: "1px solid #e5e7eb", background: "white", cursor: "pointer" },

  label: { fontSize: 12, fontWeight: 800, color: "#334155" },
  input: { width: "100%", padding: 10, borderRadius: 12, border: "1px solid #e5e7eb", outline: "none" },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },

  overlay: { position: "fixed", inset: 0, background: "rgba(15,23,42,0.45)", display: "grid", placeItems: "center", padding: 16, zIndex: 50 },
  modal: { width: "min(920px, 100%)", background: "white", borderRadius: 18, border: "1px solid #e5e7eb", overflow: "hidden" },
  modalHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: 12, borderBottom: "1px solid #e5e7eb" },
  modalBody: { padding: 12 },
};









