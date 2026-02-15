import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../providers/AuthProvider";

export default function Units() {
  const { token } = useAuth();
  const [params, setParams] = useSearchParams();

  const [properties, setProperties] = useState([]);
  const [units, setUnits] = useState([]);

  const [includeInactive, setIncludeInactive] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const propertyId = useMemo(() => {
    const v = params.get("property_id");
    return v ? Number(v) : null;
  }, [params]);

  const [form, setForm] = useState({
    unit_number: "",
    bedrooms: 1,
    bathrooms: 1,
    sqft: "",
    rent: "",
    notes: "",
  });

  async function loadProperties() {
    const list = await api.listProperties(token, { includeInactive: false });
    setProperties(Array.isArray(list) ? list : []);
  }

  async function loadUnits(pid) {
    if (!pid) {
      setUnits([]);
      return;
    }
    const list = await api.listUnits(token, { propertyId: pid, includeInactive });
    setUnits(Array.isArray(list) ? list : []);
  }

  async function loadAll() {
    if (!token) return;
    setErr("");
    setBusy(true);
    try {
      await loadProperties();
      await loadUnits(propertyId);
    } catch (e) {
      setErr(e?.message || "Failed to load units");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, includeInactive, propertyId]);

  function pickProperty(e) {
    const pid = e.target.value ? Number(e.target.value) : "";
    if (!pid) {
      setParams({});
      return;
    }
    setParams({ property_id: String(pid) });
  }

  function onChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  const canCreate = propertyId && form.unit_number.trim();

  async function createUnit(e) {
    e.preventDefault();
    if (!canCreate) return;

    setErr("");
    setBusy(true);
    try {
      await api.createUnit(token, {
        property_id: propertyId,
        unit_number: form.unit_number.trim(),
        bedrooms: Number(form.bedrooms) || 0,
        bathrooms: Number(form.bathrooms) || 0,
        sqft: form.sqft === "" ? null : Number(form.sqft),
        rent: form.rent === "" ? null : Number(form.rent),
        notes: form.notes.trim() || null,
      });

      setForm({
        unit_number: "",
        bedrooms: 1,
        bathrooms: 1,
        sqft: "",
        rent: "",
        notes: "",
      });

      await loadUnits(propertyId);
    } catch (e2) {
      setErr(e2?.message || "Failed to create unit");
    } finally {
      setBusy(false);
    }
  }

  async function toggleActive(u) {
    setErr("");
    setBusy(true);
    try {
      if (u.is_active) await api.deactivateUnit(token, u.id);
      else await api.activateUnit(token, u.id);
      await loadUnits(propertyId);
    } catch (e) {
      setErr(e?.message || "Failed to update unit");
    } finally {
      setBusy(false);
    }
  }

  if (!token) return null;

  return (
    <div>
      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Units</h2>

        <label className="muted" style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          <input type="checkbox" checked={includeInactive} onChange={(e) => setIncludeInactive(e.target.checked)} />
          Show inactive
        </label>

        <button className="btn" onClick={loadAll} disabled={busy}>
          Refresh
        </button>
      </div>

      {err ? <div className="card" style={{ borderColor: "rgba(239,68,68,0.35)" }}>{err}</div> : null}

      <div style={{ display: "grid", gridTemplateColumns: "420px 1fr", gap: 14 }}>
        <div className="card">
          <div style={{ fontWeight: 900, marginBottom: 10 }}>Select property</div>

          <select className="input" value={propertyId || ""} onChange={pickProperty}>
            <option value="">â€” Choose â€”</option>
            {properties.map((p) => (
              <option key={p.id} value={p.id}>
                #{p.id} â€” {p.name}
              </option>
            ))}
          </select>

          <div style={{ height: 14 }} />

          <div style={{ fontWeight: 900, marginBottom: 10 }}>Add unit</div>
          <form onSubmit={createUnit}>
            <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Unit number</label>
            <input className="input" name="unit_number" value={form.unit_number} onChange={onChange} placeholder="e.g. 1A" />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
              <div>
                <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Bedrooms</label>
                <input className="input" name="bedrooms" value={form.bedrooms} onChange={onChange} />
              </div>
              <div>
                <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Bathrooms</label>
                <input className="input" name="bathrooms" value={form.bathrooms} onChange={onChange} />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
              <div>
                <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Sqft</label>
                <input className="input" name="sqft" value={form.sqft} onChange={onChange} />
              </div>
              <div>
                <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Rent</label>
                <input className="input" name="rent" value={form.rent} onChange={onChange} />
              </div>
            </div>

            <div style={{ marginTop: 10 }}>
              <label className="muted" style={{ fontSize: 12, fontWeight: 700 }}>Notes</label>
              <textarea className="input" name="notes" value={form.notes} onChange={onChange} rows={3} />
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
              <button className="btn primary" type="submit" disabled={!canCreate || busy}>
                Create
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div style={{ fontWeight: 900, marginBottom: 10 }}>
            Units {propertyId ? `for property #${propertyId}` : ""}
          </div>

          {!propertyId ? (
            <div className="muted">Pick a property to load units.</div>
          ) : units.length === 0 ? (
            <div className="muted">No units yet.</div>
          ) : (
            <div style={{ display: "grid", gap: 10 }}>
              {units.map((u) => (
                <div
                  key={u.id}
                  className="card"
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    opacity: u.is_active ? 1 : 0.6,
                  }}
                  <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <div style={{ fontWeight: 900 }}>
                      Unit {u.unit_number} {!u.is_active ? <span className="muted">(inactive)</span> : null}
                    </div>
                    <div className="muted" style={{ marginLeft: "auto", fontSize: 13 }}>
                      {u.bedrooms} bd â€¢ {u.bathrooms} ba â€¢ {u.sqft ?? "â€”"} sqft â€¢ rent {u.rent ?? "â€”"}
                    </div>

                    <button
                      className={"btn " + (u.is_active ? "danger" : "primary")}
                      onClick={() => toggleActive(u)}
                      disabled={busy}
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </div>

                  {u.notes ? <div className="muted" style={{ marginTop: 6 }}>{u.notes}</div> : null}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

