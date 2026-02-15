import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useAuth } from "../providers/AuthProvider";

const emptyForm = {
  name: "",
  address1: "",
  address2: "",
  city: "",
  state: "",
  zip: "",
  notes: "",
};

export default function Properties() {
  const { token } = useAuth();

  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);

  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null); // property object
  const [form, setForm] = useState({ ...emptyForm });

  const isEditing = !!selected;

  async function refresh() {
    if (!token) return;
    setLoading(true);
    setErr("");
    try {
      const data = await api.listProperties(token, { includeInactive });
      setItems(Array.isArray(data) ? data : []);
      // if selected was deactivated/removed, keep selection if still exists
      if (selected) {
        const still = (data || []).find((p) => p.id === selected.id) || null;
        setSelected(still);
        if (still) setForm(toForm(still));
      }
    } catch (e) {
      setErr(e?.message || "Failed to load properties");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, includeInactive]);

  const activeCount = useMemo(
    () => items.filter((p) => p.is_active).length,
    [items]
  );

  function toForm(p) {
    return {
      name: p.name ?? "",
      address1: p.address1 ?? "",
      address2: p.address2 ?? "",
      city: p.city ?? "",
      state: p.state ?? "",
      zip: p.zip ?? "",
      notes: p.notes ?? "",
    };
  }

  function onSelect(p) {
    setSelected(p);
    setForm(toForm(p));
    setErr("");
  }

  function onNew() {
    setSelected(null);
    setForm({ ...emptyForm });
    setErr("");
  }

  function setField(k, v) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function onSave(e) {
    e?.preventDefault?.();
    if (!token) return;

    setErr("");

    // tiny validation
    if (!form.name.trim()) return setErr("Name is required.");
    if (!form.address1.trim()) return setErr("Address1 is required.");
    if (!form.city.trim()) return setErr("City is required.");
    if (!form.state.trim()) return setErr("State is required.");
    if (!form.zip.trim()) return setErr("Zip is required.");

    try {
      if (isEditing) {
        const updated = await api.updateProperty(token, selected.id, {
          ...form,
          notes: form.notes?.trim() ? form.notes : null,
          address2: form.address2?.trim() ? form.address2 : null,
        });
        // refresh list + keep selection
        await refresh();
        setSelected(updated);
        setForm(toForm(updated));
      } else {
        const created = await api.createProperty(token, {
          ...form,
          notes: form.notes?.trim() ? form.notes : null,
          address2: form.address2?.trim() ? form.address2 : null,
        });
        await refresh();
        setSelected(created);
        setForm(toForm(created));
      }
    } catch (e2) {
      setErr(e2?.message || "Save failed");
    }
  }

  async function onDeactivate() {
    if (!token || !selected) return;
    setErr("");
    try {
      await api.deactivateProperty(token, selected.id);
      await refresh();
    } catch (e) {
      setErr(e?.message || "Deactivate failed");
    }
  }

  async function onActivate() {
    if (!token || !selected) return;
    setErr("");
    try {
      await api.activateProperty(token, selected.id);
      await refresh();
    } catch (e) {
      setErr(e?.message || "Activate failed");
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 14 }}>
      {/* Left: list */}
      <div className="card">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ fontWeight: 800, fontSize: 16 }}>Properties</div>
          <div className="muted" style={{ fontSize: 12 }}>
            {loading ? "Loadingâ€¦" : `${activeCount}/${items.length} active`}
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <button className="btn primary" onClick={onNew}>
              + New
            </button>
          </div>
        </div>

        <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 10 }}>
          <label className="muted" style={{ fontSize: 13, display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
            />
            Show inactive
          </label>

          <button className="btn" style={{ marginLeft: "auto" }} onClick={refresh}>
            Refresh
          </button>
        </div>

        {err ? (
          <div style={{ marginTop: 10 }} className="card">
            <div style={{ color: "rgba(251,113,133,0.95)", fontWeight: 700 }}>
              {err}
            </div>
          </div>
        ) : null}

        <div style={{ marginTop: 10, display: "grid", gap: 10 }}>
          {!loading && items.length === 0 ? (
            <div className="card" style={{ background: "rgba(255,255,255,0.03)" }}>
              <div style={{ fontWeight: 800 }}>No properties yet</div>
              <div className="muted" style={{ marginTop: 6 }}>
                Click <b>New</b> to add your first property.
              </div>
            </div>
          ) : null}

          {items.map((p) => {
            const isSel = selected?.id === p.id;
            return (
              <button
                key={p.id}
                onClick={() => onSelect(p)}
                className="card"
                style={{
                  textAlign: "left",
                  cursor: "pointer",
                  padding: 12,
                  background: isSel ? "rgba(96,165,250,0.14)" : "rgba(255,255,255,0.04)",
                  borderColor: isSel ? "rgba(96,165,250,0.35)" : "rgba(255,255,255,0.10)",
                }}
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ fontWeight: 800 }}>{p.name}</div>
                  <div
                    className="hr-pill"
                    style={{
                      marginLeft: "auto",
                      borderColor: p.is_active ? "rgba(52,211,153,0.35)" : "rgba(251,113,133,0.35)",
                      background: p.is_active ? "rgba(52,211,153,0.10)" : "rgba(251,113,133,0.10)",
                      color: p.is_active ? "rgba(52,211,153,0.95)" : "rgba(251,113,133,0.95)",
                    }}
                    {p.is_active ? "Active" : "Inactive"}
                  </div>
                </div>
                <div className="muted" style={{ marginTop: 6, fontSize: 13 }}>
                  {p.address1}
                  {p.address2 ? `, ${p.address2}` : ""} â€” {p.city}, {p.state} {p.zip}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: editor */}
      <div className="card">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ fontWeight: 800, fontSize: 16 }}>
            {isEditing ? `Edit Property #${selected.id}` : "New Property"}
          </div>
          <div className="muted" style={{ fontSize: 12 }}>
            {isEditing ? "Update details and save" : "Fill out details and create"}
          </div>

          {isEditing ? (
            <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
              {selected?.is_active ? (
                <button className="btn danger" onClick={onDeactivate}>
                  Deactivate
                </button>
              ) : (
                <button className="btn primary" onClick={onActivate}>
                  Activate
                </button>
              )}
            </div>
          ) : null}
        </div>

        <form onSubmit={onSave} style={{ marginTop: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <div style={{ gridColumn: "1 / -1" }}>
              <label className="muted" style={{ fontSize: 12 }}>Name</label>
              <input className="input" value={form.name} onChange={(e) => setField("name", e.target.value)} />
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label className="muted" style={{ fontSize: 12 }}>Address 1</label>
              <input className="input" value={form.address1} onChange={(e) => setField("address1", e.target.value)} />
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label className="muted" style={{ fontSize: 12 }}>Address 2 (optional)</label>
              <input className="input" value={form.address2} onChange={(e) => setField("address2", e.target.value)} />
            </div>

            <div>
              <label className="muted" style={{ fontSize: 12 }}>City</label>
              <input className="input" value={form.city} onChange={(e) => setField("city", e.target.value)} />
            </div>

            <div>
              <label className="muted" style={{ fontSize: 12 }}>State</label>
              <input className="input" value={form.state} onChange={(e) => setField("state", e.target.value)} />
            </div>

            <div>
              <label className="muted" style={{ fontSize: 12 }}>Zip</label>
              <input className="input" value={form.zip} onChange={(e) => setField("zip", e.target.value)} />
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label className="muted" style={{ fontSize: 12 }}>Notes (optional)</label>
              <textarea
                className="input"
                rows={4}
                value={form.notes}
                onChange={(e) => setField("notes", e.target.value)}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
            <button className="btn primary" type="submit">
              {isEditing ? "Save Changes" : "Create Property"}
            </button>
            <button className="btn" type="button" onClick={onNew}>
              Clear
            </button>

            <div className="muted" style={{ marginLeft: "auto", fontSize: 12, alignSelf: "center" }}>
              {isEditing ? "Changes save to your local SQLite DB." : "Create then add Units."}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

