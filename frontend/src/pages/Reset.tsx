import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError, type Detail } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout, Message } from "./AuthLayout";

/** Without ?token= : request a reset link. With ?token= : set the new
 * password (the mode the emailed link lands on). */
export default function Reset() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  return token ? <Confirm token={token} /> : <Request />;
}

function Request() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<{ kind: "ok" | "err" | ""; text: string }>({ kind: "", text: "" });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await api<Detail>("/auth/password-reset/request", { method: "POST", body: { email } });
      setMessage({ kind: "ok", text: `${res.detail} (dev mode: see the server terminal)` });
    } catch (err) {
      setMessage({ kind: "err", text: err instanceof ApiError ? err.message : "network error" });
    }
  }

  return (
    <AuthLayout title="Reset password">
      <form onSubmit={submit} className="space-y-3">
        <div className="space-y-1">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" required value={email}
                 onChange={(e) => setEmail(e.target.value)} />
        </div>
        <Button type="submit" className="w-full">Send reset link</Button>
      </form>
      <Message kind={message.kind} text={message.text} />
      <div className="text-xs">
        <Link className="text-primary hover:underline" to="/login">Back to sign in</Link>
      </div>
    </AuthLayout>
  );
}

function Confirm({ token }: { token: string }) {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api<void>("/auth/password-reset/confirm", {
        method: "POST", body: { token, new_password: password },
      });
      navigate("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "network error");
    }
  }

  return (
    <AuthLayout title="Choose a new password">
      <form onSubmit={submit} className="space-y-3">
        <div className="space-y-1">
          <Label htmlFor="password">New password (10+ characters)</Label>
          <Input id="password" type="password" autoComplete="new-password" required minLength={10}
                 value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <Button type="submit" className="w-full">Set password</Button>
      </form>
      <Message kind="err" text={error} />
    </AuthLayout>
  );
}
