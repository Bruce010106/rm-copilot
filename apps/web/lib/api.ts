// Server-side client for the agent service. Only used in Server Components,
// so AGENT_API_URL never reaches the browser.

// Types are generated from the FastAPI OpenAPI schema: run `pnpm gen:api` after backend changes.
import type { components } from "./api-types";

const BASE = process.env.AGENT_API_URL ?? "http://localhost:8000";

type Schemas = components["schemas"];
export type CustomerSummary = Schemas["CustomerSummary"];
export type CustomerPage = Schemas["CustomerPage"];
export type CustomerDetail = Schemas["CustomerDetail"];

async function get<T>(path: string): Promise<T | null> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`agent service ${res.status} on ${path}`);
  return res.json() as Promise<T>;
}

export function listCustomers(params: Record<string, string | undefined>) {
  const qs = new URLSearchParams(
    Object.entries(params).filter((e): e is [string, string] => Boolean(e[1])),
  );
  return get<CustomerPage>(`/customers?${qs}`) as Promise<CustomerPage>;
}

export function getCustomer(id: string) {
  return get<CustomerDetail>(`/customers/${encodeURIComponent(id)}`);
}

export function formatWan(amount: string | number) {
  return `${(Number(amount) / 10_000).toLocaleString("zh-CN", { maximumFractionDigits: 1 })} 万`;
}
