import api from "./api";

export async function getLeaseRules(stateCode) {
  const { data } = await api.get(`/lease-builder/rules/${stateCode}`);
  return data;
}

export async function renderLeaseDraft(payload) {
  const { data } = await api.post(`/lease-builder/render`, payload);
  return data;
}
