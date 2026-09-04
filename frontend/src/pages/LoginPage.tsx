import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/AuthContext";

const accounts = [
  { role: "Fleet manager", email: "manager@fleetmind.demo" },
  { role: "Technician", email: "technician@fleetmind.demo" },
];

export default function LoginPage() {
  const { login, createViewer, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(accounts[0].email);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"login" | "register" | "verify">("login");
  const [name, setName] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [code, setCode] = useState("");
  const destination = (location.state as { from?: string } | null)?.from ?? "/";

  if (isLoading) return <div className="app-loading">Validating your secure session…</div>;
  if (isAuthenticated) return <Navigate to="/" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(destination, { replace: true });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Sign in failed.");
    } finally {
      setLoading(false);
    }
  };

  const chooseAccount = (index: number) => {
    setEmail(accounts[index].email);
    setPassword("");
    setError("");
  };

  const register = (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (name.trim().length < 2) return setError("Enter your full name.");
    if (password.length < 12) return setError("Password must contain at least 12 characters.");
    if (password !== confirmation) return setError("Passwords do not match.");
    setMode("verify");
  };

  const verify = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await createViewer(name, email, password, code);
      navigate("/", { replace: true });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Account creation failed.");
    } finally { setLoading(false); }
  };

  return (
    <main className="login-page">
      <section className="login-visual" aria-label="FleetMind intelligent mobility">
        <img src="/fleetmind-vehicle.png" alt="Electric fleet vehicle at sunset" />
        <div className="login-visual-shade" />
        <div className="login-brand">
          <span className="login-logo"><svg viewBox="0 0 48 48"><path d="M8 31 17 14l7 13 7-13 9 17"/><path d="M8 31h10l3-6 5 11 4-8h10"/></svg></span>
          <strong>FleetMind</strong>
        </div>
        <div className="login-message"><span>FLEETMIND ONE</span><h1>Intelligence that<br/>keeps you moving.</h1><p>Predict risk. Protect uptime. Make every fleet decision with confidence.</p></div>
        <div className="login-live"><i /> Protected operations workspace</div>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <span className="login-eyebrow">{mode === "login" ? "SECURE ACCESS" : mode === "register" ? "VIEWER REGISTRATION" : "EMAIL VERIFICATION"}</span>
          <h2>{mode === "login" ? "Welcome back" : mode === "register" ? "Create account" : "Check your email"}</h2>
          <p>{mode === "login" ? "Sign in to your fleet operations workspace." : mode === "register" ? "Create a read-only viewer account." : `Enter the six-digit code sent to ${email}.`}</p>
          {mode === "login" && <form onSubmit={submit}>
            <label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label>
            <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required /></label>
            {error && <div className="login-error">{error}</div>}
            <button type="submit" disabled={loading}>{loading ? "Signing in…" : "Sign in"}</button>
          </form>}
          {mode === "register" && <form onSubmit={register}>
            <label>Full name<input value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" required /></label>
            <label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required /></label>
            <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" minLength={12} required /><small>12+ characters with upper-case, lower-case, number, and symbol.</small></label>
            <label>Confirm password<input type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" required /></label>
            {error && <div className="login-error">{error}</div>}
            <button type="submit">Continue to verification</button>
          </form>}
          {mode === "verify" && <form onSubmit={verify}>
            <div className="demo-code"><span>DEMO VERIFICATION CODE</span><strong>482913</strong><small>Amazon Cognito will email this code in production.</small></div>
            <label>Verification code<input inputMode="numeric" maxLength={6} value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ""))} placeholder="000000" required /></label>
            {error && <div className="login-error">{error}</div>}
            <button type="submit" disabled={loading}>{loading ? "Creating account…" : "Verify and create viewer"}</button>
          </form>}
          {mode === "login" && <button className="account-switch" type="button" onClick={() => { setMode("register"); setName(""); setEmail(""); setPassword(""); setError(""); }}>New viewer? Create an account</button>}
          {mode !== "login" && <button className="account-switch" type="button" onClick={() => { setMode("login"); setError(""); }}>Back to sign in</button>}
          {mode === "login" && <div className="demo-access"><span>COMPANY TEST ACCOUNTS</span><div>{accounts.map((account, index) => <button key={account.role} type="button" onClick={() => chooseAccount(index)}>{account.role}</button>)}</div><small>Select an account, then enter its company-issued password.</small></div>}
          <footer><span className="lock-mark">⌁</span> Signed session · server-enforced role access</footer>
        </div>
      </section>
    </main>
  );
}
