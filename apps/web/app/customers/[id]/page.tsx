import Link from "next/link";
import { notFound } from "next/navigation";
import { formatWan, getCustomer } from "@/lib/api";

export default async function CustomerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = await getCustomer(id);
  if (!c) notFound();

  const age = new Date().getFullYear() - Number(c.birth_date.slice(0, 4));
  const facts: [string, string][] = [
    ["等级", c.tier],
    ["AUM", formatWan(c.aum)],
    ["风险等级", c.risk_level],
    ["城市", c.city],
    ["职业", c.occupation],
    ["年龄", `${age}`],
    ["客户经理", c.rm_name],
    ["开户", c.onboarded_at],
  ];

  return (
    <div className="space-y-6">
      <div>
        <Link href="/customers" className="text-sm text-[var(--muted)]">
          ← 客户列表
        </Link>
        <h1 className="mt-1 text-xl font-semibold">
          {c.name} <span className="text-sm font-normal text-[var(--muted)]">{c.id}</span>
        </h1>
      </div>

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {facts.map(([k, v]) => (
          <div key={k} className="rounded border border-[var(--border)] bg-[var(--card)] p-3">
            <div className="text-xs text-[var(--muted)]">{k}</div>
            <div className="mt-1 font-medium">{v}</div>
          </div>
        ))}
      </section>

      <section className="rounded border border-dashed border-[var(--border)] p-4 text-sm text-[var(--muted)]">
        AI 摘要（带证据引用）将在 W3 接入。
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section>
          <h2 className="mb-2 font-semibold">持仓</h2>
          <ul className="divide-y divide-[var(--border)] rounded border border-[var(--border)] bg-[var(--card)] text-sm">
            {c.holdings.map((h) => (
              <li key={h.id} className="flex justify-between gap-3 px-3 py-2">
                <div>
                  <div>{h.product_name}</div>
                  <div className="text-xs text-[var(--muted)]">
                    {h.category}
                    {h.maturity_date && ` · 到期 ${h.maturity_date}`}
                  </div>
                </div>
                <div className="tabular-nums">{formatWan(h.amount)}</div>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2 className="mb-2 font-semibold">服务记录</h2>
          <ol className="space-y-2 text-sm">
            {c.interactions.map((i) => (
              <li key={i.id} className="rounded border border-[var(--border)] bg-[var(--card)] px-3 py-2">
                <div className="text-xs text-[var(--muted)]">
                  {i.occurred_at.replace("T", " ").slice(0, 16)} · {i.channel} · {i.id}
                </div>
                <div className="mt-1">{i.content}</div>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}
