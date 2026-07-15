import { useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError, type Detail } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout, Message } from "./AuthLayout";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<{ kind: "ok" | "err" | ""; text: string }>({ kind: "", text: "" });
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const res = await api<Detail>("/auth/register", { method: "POST", body: { email, password } });
      setMessage({ kind: "ok", text: res.detail });
    } catch (err) {
      setMessage({ kind: "err", text: err instanceof ApiError ? err.message : "network error" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout title="Create account">
      <form onSubmit={submit} className="space-y-3">
        <div className="space-y-1">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="username" required
                 value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label htmlFor="password">Password (10+ characters)</Label>
          <Input id="password" type="password" autoComplete="new-password" required minLength={10}
                 value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <Button type="submit" className="w-full" disabled={busy}>
          {busy ? "Registering…" : "Register"}
        </Button>
      </form>
      <Message kind={message.kind} text={message.text} />
      {message.kind === "ok" && (
        <p className="text-xs text-muted-foreground">
          Dev mode: the verification link is printed in the server terminal
          (no real email is sent yet).
        </p>
      )}
      <div className="text-xs">
        <Link className="text-primary hover:underline" to="/login">Sign in instead</Link>
      </div>
    </AuthLayout>
  );
}
