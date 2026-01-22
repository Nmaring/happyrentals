import api from "./api";

export async function listPayments(params = {}) {
  const res = await api.get("/payments", { params });
  return res.data;
}

export async function createPayment(payload) {
  const res = await api.post("/payments", payload);
  return res.data;
}

export async function updatePayment(id, payload) {
  const res = await api.put(`/payments/${id}`, payload);
  return res.data;
}

