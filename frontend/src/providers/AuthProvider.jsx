import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("hr_token") || "");
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("hr_email") || "");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // mark boot complete
    setLoading(false);
  }, []);

  async function login(email, password) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("hr_token", data.access_token);
    localStorage.setItem("hr_email", email);
    setToken(data.access_token);
    setUserEmail(email);
    return data;
  }

  async function register(email, password) {
    const data = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    return data;
  }

  function logout() {
    localStorage.removeItem("hr_token");
    localStorage.removeItem("hr_email");
    setToken("");
    setUserEmail("");
  }

  const value = useMemo(
    () => ({ token, userEmail, loading, login, register, logout }),
    [token, userEmail, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


