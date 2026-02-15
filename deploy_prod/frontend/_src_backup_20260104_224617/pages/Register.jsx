import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../providers/AuthProvider";

export default function Register() {
  const nav = useNavigate();
  const { token, register, login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (token) nav("/properties", { replace: true });
  }, [token, nav]);

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      await register(email.trim(), password);
      await login(email.trim(), password);
      nav("/properties", { replace: true });
    } catch (e2) {
      setErr(e2.message || "Register failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-container">
      <div className="card" style={{ maxWidth: 520, margin: "40px auto" }}>
        <div className="card-title">Register</div>

        {err && <div className="error">{err}</div>}

        <form onSubmit={onSubmit} className="stack">
          <div className="field">
            <label>Email</label>
            <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>

          <div className="field">
            <label>Password</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="small" style={{ marginTop: 6 }}>
              Use 8+ characters.
            </div>
          </div>

          <button className="btn btn-primary" type="submit" disabled={busy}>
            {busy ? "Creatingâ€¦" : "Create account"}
          </button>

          <div className="small">
            Already have an account? <Link to="/login">Login</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
