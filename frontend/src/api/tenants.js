// frontend/src/api/tenants.js
import api from "./api.js";

export async function listTenants(q = "") {
  const params = {};
  if (q && q.trim()) params.q = q.trim();
  const { data } = await api.get("/tenants", { params });
  return data;
}

export async function createTenant(payload) {
  const { data } = await api.post("/tenants", payload);
  return data;
}

export async function updateTenant(id, payload) {
  const { data } = await api.put(`/tenants/${id}`, payload);
  return data;
}

export async function deleteTenant(id) {
  const { data } = await api.delete(`/tenants/${id}`);
  return data;
}


