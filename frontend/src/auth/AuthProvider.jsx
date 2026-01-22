import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("hr_token") || "");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadMe(tk) {
    if (!tk) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await apiFetch("/auth/me", { token: tk });
      setUser(me);
    } catch {
      setUser(null);
      setToken("");
      localStorage.removeItem("hr_token");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMe(token);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email, password) {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setToken(res.access_token);
    localStorage.setItem("hr_token", res.access_token);
    await loadMe(res.access_token);
  }

  async function register(email, password) {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    // After register, auto-login
    await login(email, password);
  }

  function logout() {
    setUser(null);
    setToken("");
    localStorage.removeItem("hr_token");
  }

  const value = useMemo(() => ({
    token,
    user,
    loading,
    login,
    register,
    logout,
  }), [token, user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}


