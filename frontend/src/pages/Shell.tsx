import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError, type Me, type Portfolio } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

/** The authenticated shell: proves the full loop (session cookie ->
 * typed API -> render). The M3 dashboard grows inside this page. */
export default function Shell() {
  const navigate = useNavigate();
  const [me, setMe] = useState<Me | null>(null);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("category_2");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setMe(await api<Me>("/api/me", { redirectOn401: true }));
    setPortfolios(await api<Portfolio[]>("/api/portfolios", { redirectOn401: true }));
  }, []);

  useEffect(() => {
    refresh().catch((err) =>
      setError(err instanceof ApiError ? err.message : "network error"));
  }, [refresh]);

  async function logout() {
    await api<void>("/auth/logout", { method: "POST" });
    navigate("/login");
  }

  async function createPortfolio(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api<Portfolio>("/api/portfolios", {
        method: "POST", body: { name, category_key: category }, redirectOn401: true,
      });
      setName("");
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "network error");
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Sunabha Agent</h1>
          <p className="text-xs text-muted-foreground">
            Signals for a human to review — nothing executes trades.
            {me && <> Signed in as <b>{me.email}</b>.</>}
          </p>
        </div>
        <Button variant="secondary" onClick={logout}>Sign out</Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Portfolios</CardTitle>
          <CardDescription>
            One committed category per portfolio (KB §6.3) — the dashboard
            will grow here.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {portfolios.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No portfolios yet — create your first one below. Pick the ONE
              category you'll commit to; the course's rule is a year of
              discipline per category.
            </p>
          ) : (
            <ul className="space-y-2">
              {portfolios.map((p) => (
                <li key={p.id} className="flex items-center justify-between rounded-md border border-border p-3 text-sm">
                  <span className="font-semibold">{p.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {p.category_key} · committed {p.commitment_started_on}
                  </span>
                </li>
              ))}
            </ul>
          )}

          <form onSubmit={createPortfolio} className="flex items-end gap-2">
            <div className="flex-1 space-y-1">
              <Label htmlFor="pname">New portfolio</Label>
              <Input id="pname" required value={name} placeholder="e.g. main"
                     onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="pcat">Category</Label>
              <select
                id="pcat"
                className="h-10 rounded-md border border-input bg-white px-2 text-sm"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {["category_1", "category_2", "category_3", "category_4"].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <Button type="submit">Create</Button>
          </form>
          {error && <p className="text-xs text-destructive">{error}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
