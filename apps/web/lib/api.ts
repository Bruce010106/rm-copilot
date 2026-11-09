// Server-side client for the agent service. Only used in Server Components,
// so AGENT_API_URL never reaches the browser.

const BASE = process.env.AGENT_API_URL ?? "http://localhost:8000";

export type CustomerSummary = {
  id: string;
  name: string;
  city: string;
  tier: string;
  risk_level: string;
  aum: string;
  rm_id: string;
  tags: string[];
};

export type CustomerPage = {
  items: CustomerSummary[];
  total: number;
  page: number;
  page_size: number;
};

export type CustomerDetail = CustomerSummary & {
  gender: string;
  birth_date: string;
  occupation: string;
  onboarded_at: string;
  rm_name: string;
  holdings: {
    id: string;
    product_id: string;
    product_name: string;
    category: string;
    amount: string;
    start_date: string;
    maturity_date: string | null;
  }[];
  interactions: { id: string; channel: string; occurred_at: string; content: string }[];
};

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
