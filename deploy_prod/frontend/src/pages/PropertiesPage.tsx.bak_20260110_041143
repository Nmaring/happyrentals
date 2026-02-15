// frontend/src/pages/PropertiesPage.jsx
import React from "react";
import {
  listProperties,
  createProperty,
  updateProperty,
  deleteProperty,
} from "../api/properties";

const EMPTY = {
  name: "",
  address1: "",
  address2: "",
  city: "",
  state: "MN",
  zip: "",
  notes: "",
};

export default function PropertiesPage() {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [editing, setEditing] = React.useState(null); // null | {id: number|null}
  const [form, setForm] = React.useState(EMPTY);

  const refresh = React.useCallback(async () => {
    setLoading(true);
    try {
      setItems(await listProperties());
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  const startNew = () => {
    setEditing({ id: null });
    setForm(EMPTY);
  };

  const startEdit = (p) => {
    setEditing(p);
    setForm({
      name: p.name ?? "",
      address1: p.address1 ?? "",
      address2: p.address2 ?? "",
      city: p.city ?? "",
      state: p.state ?? "MN",
      zip: p.zip ?? "",
      notes: p.notes ?? "",
    });
  };

  const save = async () => {
    const payload = {
      name: form.name.trim(),
      address1: form.address1.trim(),
      address2: form.address2.trim() ? form.address2.trim() : null,
      city: form.city.trim(),
      state: form.state.trim(),
      zip: form.zip.trim(),
      notes: form.notes.trim() ? form.notes.trim() : null,
    };

    if (!payload.name || !payload.address1 || !payload.city || !payload.state || !payload.zip) {
      alert("Name, Address, City, State, ZIP are required.");
      return;
    }

    if (editing?.id) await updateProperty(editing.id, payload);
    else await createProperty(payload);

    setEditing(null);
    await refresh();
  };

  const remove = async (id) => {
    if (!confirm("Delete this property?")) return;
    await deleteProperty(id);
    await refresh();
  };

  return (
    <div className="h-full min-h-0 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Properties</h1>
        <button className="px-3 py-2 rounded-lg bg-black text-white" onClick={startNew}>
          + New Property
        </button>
      </div>

      <div className="flex gap-4 min-h-0 flex-1">
        {/* List */}
        <div className="w-[420px] max-w-full overflow-auto rounded-xl border bg-white">
          {loading ? (
            <div className="p-4 text-sm opacity-70">Loadingâ€¦</div>
          ) : items.length === 0 ? (
            <div className="p-4 text-sm opacity-70">No properties yet.</div>
          ) : (
            <ul className="divide-y">
              {items.map((p) => (
                <li key={p.id} className="p-3 hover:bg-gray-50">
                  <div className="flex items-start justify-between gap-3">
                    <button className="text-left flex-1" onClick={() => startEdit(p)}>
                      <div className="font-medium">{p.name}</div>
                      <div className="text-sm opacity-70">
                        {p.address1}
                        {p.city ? `, ${p.city}` : ""}
                        {p.state ? ` ${p.state}` : ""}
                        {p.zip ? ` ${p.zip}` : ""}
                      </div>
                    </button>
                    <button
                      className="text-sm opacity-70 hover:opacity-100"
                      onClick={() => remove(p.id)}
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Editor */}
        <div className="flex-1 rounded-xl border bg-white p-4 overflow-auto">
          {!editing ? (
            <div className="text-sm opacity-70">Select a property or create a new one.</div>
          ) : (
            <div className="max-w-xl flex flex-col gap-3">
              <div className="text-lg font-semibold">
                {editing.id ? "Edit Property" : "New Property"}
              </div>

              {["name", "address1", "address2", "city", "state", "zip"].map((k) => (
                <label key={k} className="flex flex-col gap-1">
                  <span className="text-sm opacity-70">{k.toUpperCase()}</span>
                  <input
                    className="border rounded-lg px-3 py-2"
                    value={form[k] ?? ""}
                    onChange={(e) => setForm((s) => ({ ...s, [k]: e.target.value }))}
                  />
                </label>
              ))}

              <label className="flex flex-col gap-1">
                <span className="text-sm opacity-70">NOTES</span>
                <textarea
                  className="border rounded-lg px-3 py-2 min-h-[110px]"
                  value={form.notes ?? ""}
                  onChange={(e) => setForm((s) => ({ ...s, notes: e.target.value }))}
                />
              </label>

              <div className="flex gap-2 pt-2">
                <button className="px-3 py-2 rounded-lg bg-black text-white" onClick={save}>
                  Save
                </button>
                <button className="px-3 py-2 rounded-lg border" onClick={() => setEditing(null)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}




