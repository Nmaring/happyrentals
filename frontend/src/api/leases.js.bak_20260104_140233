import api from "./api";

// GET /leases?tenant_id=&unit_id=
export async function fetchLeases(params = {}) {
  const { tenant_id, unit_id } = params;
  const qs = new URLSearchParams();
  if (tenant_id) qs.set("tenant_id", String(tenant_id));
  if (unit_id) qs.set("unit_id", String(unit_id));
  const url = qs.toString() ? `/leases?${qs.toString()}` : "/leases";
  const res = await api.get(url);
  return res.data;
}

export async function createLease(payload) {
  const res = await api.post("/leases", payload);
  return res.data;
}

export async function updateLease(id, payload) {
  const res = await api.put(`/leases/${id}`, payload);
  return res.data;
}

export async function deleteLease(id) {
  const res = await api.delete(`/leases/${id}`);
  return res.data;
}
