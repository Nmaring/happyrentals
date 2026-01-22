// frontend/src/api/properties.js
import api from "./api.js";

export async function listProperties() {
  const { data } = await api.get("/properties");
  return data;
}

export async function createProperty(payload) {
  const { data } = await api.post("/properties", payload);
  return data;
}

export async function updateProperty(id, payload) {
  const { data } = await api.put(`/properties/${id}`, payload);
  return data;
}

export async function deleteProperty(id) {
  const { data } = await api.delete(`/properties/${id}`);
  return data;
}
