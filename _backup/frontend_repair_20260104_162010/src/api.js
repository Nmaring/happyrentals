const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function apiFetch(path, { token, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const text = await res.text();

  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text || null;
  }

  if (!res.ok) {
    const msg = data?.detail || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  // --- Health ---
  health: () => apiFetch("/health"),

  // --- Properties ---
  listProperties: (token, { includeInactive = false } = {}) =>
    apiFetch(`/properties?include_inactive=${includeInactive ? "true" : "false"}`, { token }),
  createProperty: (token, payload) =>
    apiFetch("/properties", { token, method: "POST", body: JSON.stringify(payload) }),
  updateProperty: (token, id, payload) =>
    apiFetch(`/properties/${id}`, { token, method: "PUT", body: JSON.stringify(payload) }),
  deactivateProperty: (token, id) => apiFetch(`/properties/${id}/deactivate`, { token, method: "POST" }),
  activateProperty: (token, id) => apiFetch(`/properties/${id}/activate`, { token, method: "POST" }),

  // --- Units ---
  // Supports BOTH call styles:
  // 1) listUnits(token, propertyId, {includeInactive})
  // 2) listUnits(token, { propertyId, includeInactive })
  listUnits: (token, arg1, arg2) => {
    let propertyId;
    let includeInactive = false;

    if (typeof arg1 === "object" && arg1 !== null) {
      propertyId = arg1.propertyId;
      includeInactive = !!arg1.includeInactive;
    } else {
      propertyId = arg1;
      includeInactive = !!(arg2 && arg2.includeInactive);
    }

    if (!propertyId) return Promise.resolve([]);
    return apiFetch(
      `/units?property_id=${propertyId}&include_inactive=${includeInactive ? "true" : "false"}`,
      { token }
    );
  },

  createUnit: (token, payload) =>
    apiFetch("/units", { token, method: "POST", body: JSON.stringify(payload) }),
  updateUnit: (token, id, payload) =>
    apiFetch(`/units/${id}`, { token, method: "PUT", body: JSON.stringify(payload) }),
  deactivateUnit: (token, id) => apiFetch(`/units/${id}/deactivate`, { token, method: "POST" }),
  activateUnit: (token, id) => apiFetch(`/units/${id}/activate`, { token, method: "POST" }),

  // --- Tenants ---
  listTenantsByUnit: (token, unitId, { includeInactive = false } = {}) =>
    apiFetch(`/tenants?unit_id=${unitId}&include_inactive=${includeInactive ? "true" : "false"}`, { token }),
  listTenantsByProperty: (token, propertyId, { includeInactive = false } = {}) =>
    apiFetch(`/tenants?property_id=${propertyId}&include_inactive=${includeInactive ? "true" : "false"}`, { token }),

  // Alias used by my Tenants page:
  // listTenants(token, { unitId, propertyId, includeInactive })
  listTenants: (token, { unitId, propertyId, includeInactive = false } = {}) => {
    if (unitId) return apiFetch(`/tenants?unit_id=${unitId}&include_inactive=${includeInactive ? "true" : "false"}`, { token });
    if (propertyId) return apiFetch(`/tenants?property_id=${propertyId}&include_inactive=${includeInactive ? "true" : "false"}`, { token });
    return Promise.resolve([]);
  },

  createTenant: (token, payload) =>
    apiFetch("/tenants", { token, method: "POST", body: JSON.stringify(payload) }),
  updateTenant: (token, id, payload) =>
    apiFetch(`/tenants/${id}`, { token, method: "PUT", body: JSON.stringify(payload) }),
  deactivateTenant: (token, id) => apiFetch(`/tenants/${id}/deactivate`, { token, method: "POST" }),
  activateTenant: (token, id) => apiFetch(`/tenants/${id}/activate`, { token, method: "POST" }),
};
