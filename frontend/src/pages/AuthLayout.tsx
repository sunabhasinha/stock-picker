import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function AuthLayout({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen place-items-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>
            Sunabha Agent — signals for a human to review. Nothing executes trades.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">{children}</CardContent>
      </Card>
    </div>
  );
}

export function Message({ kind, text }: { kind: "ok" | "err" | ""; text: string }) {
  if (!text) return <p className="min-h-5 text-xs" />;
  return (
    <p className={`min-h-5 text-xs ${kind === "ok" ? "text-success" : "text-destructive"}`}>
      {text}
    </p>
  );
}
