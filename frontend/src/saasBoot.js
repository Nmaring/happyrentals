const TOKEN_KEY = "hr_token";

export async function saasBoot() {
  const path = window.location.pathname || "/";
  const search = window.location.search || "";
  const isLogin = path.startsWith("/login");

  let token = "";
  try { token = localStorage.getItem(TOKEN_KEY) || ""; } catch {}

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  try {
    const r = await fetch("/api/auth/me", { headers });

    // Local EXE mode: auth endpoints don't exist
    if (r.status === 404 || r.status === 405) return { mode: "local", authed: true };

    // SaaS: already authed
    if (r.status === 200) return { mode: "saas", authed: true };

    // SaaS: not authed → go login
    if (r.status === 401) {
      if (!isLogin) {
        const next = encodeURIComponent(path + search);
        window.location.replace(`/login?next=${next}`);
      }
      return { mode: "saas", authed: false };
    }

    // anything else → treat as not authed
    if (!isLogin) {
      const next = encodeURIComponent(path + search);
      window.location.replace(`/login?next=${next}`);
    }
    return { mode: "saas", authed: false };
  } catch {
    // if server is down, still let the UI load (it will show errors)
    return { mode: "unknown", authed: false };
  }
}
