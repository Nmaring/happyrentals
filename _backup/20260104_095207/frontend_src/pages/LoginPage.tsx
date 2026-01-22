import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, setAuthToken } from "../api";

export const LoginPage: React.FC = () => {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null); setBusy(true);
    try {
      const res = await login(email, password);
      setAuthToken(res.data.access_token);
      nav("/dashboard");
    } catch (e:any) {
      setErr(e?.response?.data?.detail || "Login failed. Is backend running?");
    } finally { setBusy(false); }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <h1 className="text-xl font-semibold">Log in</h1>
        <p className="text-sm text-slate-600 mt-1">Use the admin user created in setup.</p>
        {err && <div className="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3">{err}</div>}
        <form className="mt-5 space-y-3" onSubmit={onSubmit}>
          <div>
            <label className="text-sm font-medium">Email</label>
            <input className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2" value={email} onChange={(e)=>setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="text-sm font-medium">Password</label>
            <input type="password" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2" value={password} onChange={(e)=>setPassword(e.target.value)} required />
          </div>
          <button disabled={busy} className="w-full rounded-lg bg-slate-900 text-white py-2 font-medium hover:bg-slate-800 disabled:opacity-60">
            {busy ? "Signing in..." : "Log in"}
          </button>
        </form>
      </div>
    </div>
  );
};
