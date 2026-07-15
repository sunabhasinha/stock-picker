// The ONE fetch wrapper (spec: no other hand-written request plumbing).
// Same-origin by construction (ADR-0007): paths are relative, cookies are
// managed by the browser - no token ever touches JavaScript.
import type { components } from "./schema";

export type Me = components["schemas"]["MeOut"];
export type Portfolio = components["schemas"]["PortfolioOut"];
export type Detail = components["schemas"]["DetailOut"];

export class ApiError extends Error {
  constructor(public status: number, detail: string) {
    super(detail);
  }
}

interface Options {
  method?: string;
  body?: unknown;
  /** Shell pages redirect to /login on 401; auth pages show the message. */
  redirectOn401?: boolean;
}

export async function api<T>(path: string, opts: Options = {}): Promise<T> {
  const res = await fetch(path, {
    method: opts.method ?? "GET",
    credentials: "same-origin",
    headers: opts.body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });
  if (res.status === 401 && opts.redirectOn401) {
    window.location.assign("/login");
    return new Promise<T>(() => {}); // navigation is imminent
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(res.status, (data as { detail?: string }).detail ?? "request failed");
  }
  return data as T;
}
