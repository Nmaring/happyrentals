const TOKEN_KEY = "hr_token";

function getToken() {
  try { return localStorage.getItem(TOKEN_KEY) || ""; } catch { return ""; }
}
function urlString(input) {
  if (typeof input === "string") return input;
  if (input && typeof input.url === "string") return input.url;
  return "";
}
function isApiUrl(url) {
  if (!url) return false;
  return url.startsWith("/api/") || url.startsWith("api/") || url.includes("/api/");
}
function isAuthUrl(url){
  return url.includes("/api/auth/");
}

const orig = window.fetch.bind(window);

window.fetch = (input, init = {}) => {
  const url = urlString(input);
  const token = getToken();

  if (isApiUrl(url)) {
    init = { credentials: "include", ...init };
    const headers = new Headers(init.headers || {});
    if (token && !headers.get("Authorization")) headers.set("Authorization", `Bearer ${token}`);
    init.headers = headers;
  }

  return orig(input, init).then((res) => {
    if (res.status === 401 && isApiUrl(url) && !isAuthUrl(url)) {
      try { localStorage.removeItem(TOKEN_KEY); } catch {}
      if (!window.location.pathname.startsWith("/login")) {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.replace(`/login?next=${next}`);
      }
    }
    return res;
  });
};
