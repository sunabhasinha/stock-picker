import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError, type Detail } from "@/api/client";
import { AuthLayout, Message } from "./AuthLayout";

export default function Verify() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [message, setMessage] = useState<{ kind: "ok" | "err" | ""; text: string }>({
    kind: "", text: token ? "Verifying…" : "",
  });

  useEffect(() => {
    if (!token) {
      setMessage({ kind: "err", text: "missing verification token" });
      return;
    }
    api<Detail>(`/auth/verify?token=${encodeURIComponent(token)}`)
      .then((res) => setMessage({ kind: "ok", text: res.detail }))
      .catch((err) =>
        setMessage({ kind: "err", text: err instanceof ApiError ? err.message : "network error" })
      );
  }, [token]);

  return (
    <AuthLayout title="Email verification">
      <Message kind={message.kind} text={message.text} />
      <div className="text-xs">
        <Link className="text-primary hover:underline" to="/login">Go to sign in</Link>
      </div>
    </AuthLayout>
  );
}
