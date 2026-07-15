import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, ApiError } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout, Message } from "./AuthLayout";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api<void>("/auth/login", { method: "POST", body: { email, password } });
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "network error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout title="Sign in">
      <form onSubmit={submit} className="space-y-3">
        <div className="space-y-1">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="username" required
                 value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" autoComplete="current-password" required
                 value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <Button type="submit" className="w-full" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </Button>
      </form>
      <Message kind="err" text={error} />
      <div className="flex justify-between text-xs">
        <Link className="text-primary hover:underline" to="/register">Create an account</Link>
        <Link className="text-primary hover:underline" to="/reset">Forgot password?</Link>
      </div>
    </AuthLayout>
  );
}
