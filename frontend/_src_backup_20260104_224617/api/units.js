// frontend/src/api/units.js
import api from "./api.js";

export async function listUnits(propertyId = null) {
  const params = {};
  if (propertyId !== null && propertyId !== "" && propertyId !== undefined) {
    params.property_id = Number(propertyId);
  }
  const { data } = await api.get("/units", { params });
  return data;
}

export async function createUnit(payload) {
  const { data } = await api.post("/units", payload);
  return data;
}

export async function updateUnit(id, payload) {
  const { data } = await api.put(`/units/${id}`, payload);
  return data;
}

export async function deleteUnit(id) {
  const { data } = await api.delete(`/units/${id}`);
  return data;
}
