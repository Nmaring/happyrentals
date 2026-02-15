import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";
import { AuthProvider } from "./providers/AuthProvider.jsx";

/* __HR_FATAL_OVERLAY__ */
function __HR_FATAL(msg) {
  try {
    document.body.innerHTML = `<div style="padding:16px;font-family:ui-monospace,Menlo,monospace;">
      <div style="background:#fff1f2;border:1px solid #fecdd3;color:#9f1239;padding:12px;border-radius:12px;">
        <div style="font-weight:900;margin-bottom:8px;">Frontend crashed</div>
        <pre style="white-space:pre-wrap;margin:0;">${msg}</pre>
      </div>
    </div>`;
  } catch {}
}
window.addEventListener("error", (e) => __HR_FATAL(String(e?.error || e?.message || e)));
window.addEventListener("unhandledrejection", (e) => __HR_FATAL(String(e?.reason || e)));

/* __HR_FETCH_PATCH__ */
(function () {
  const API_PREFIX = "/api";
  const apiRoots = ["/properties", "/units", "/leases", "/payments", "/tenants"];

  function shouldRewrite(url) {
    if (!url || typeof url !== "string") return false;
    if (!url.startsWith("/")) return false;
    if (url.startsWith("/api/")) return false;
    if (url.startsWith("/assets/")) return false;

    return apiRoots.some((p) => url === p || url.startsWith(p + "/") || url.startsWith(p + "?"));
  }

  const origFetch = window.fetch.bind(window);

  window.fetch = (input, init) => {
    try {
      if (typeof input === "string") {
        if (shouldRewrite(input)) input = API_PREFIX + input;
        return origFetch(input, init);
      }
      // Request object
      const url = input.url || "";
      if (shouldRewrite(url)) {
        const next = new Request(API_PREFIX + url, input);
        return origFetch(next, init);
      }
      return origFetch(input, init);
    } catch (e) {
      return origFetch(input, init);
    }
  };
})();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);





