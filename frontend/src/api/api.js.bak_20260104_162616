// frontend/src/api/api.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// Attach a user-friendly message to errors (FastAPI often returns {detail: ...})
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail =
      err?.response?.data?.detail ??
      err?.response?.data?.message ??
      err?.response?.data ??
      err?.message ??
      "Request failed";

    // Make it visible to the UI code that reads e.userMessage
    err.userMessage = typeof detail === "string" ? detail : JSON.stringify(detail);

    throw err;
  }
);

export default api;
