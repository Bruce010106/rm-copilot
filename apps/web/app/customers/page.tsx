import Link from "next/link";
import { formatWan, listCustomers } from "@/lib/api";

const TIERS = ["钻石", "铂金", "黄金", "普通"];

type SearchParams = Promise<{ q?: string; tier?: string; page?: string }>;

export default async function CustomersPage({ searchParams }: { searchParams: SearchParams }) {
  const { q, tier, page = "1" } = await searchParams;
  const data = await listCustomers({ q, tier, page, page_size: "20" });
  const pageNum = Number(page);
  const lastPage = Math.max(1, Math.ceil(data.total / data.page_size));

  const href = (p: number) =>
    `/customers?${new URLSearchParams({ ...(q && { q }), ...(tier && { tier }), page: String(p) })}`;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-xl font-semibold">客户（{data.total}）</h1>
        <form className="flex flex-wrap gap-2 text-sm">
          <input
            name="q"
            defaultValue={q}
            placeholder="姓名或客户 ID"
            className="rounded border border-[var(--border)] bg-[var(--card)] px-3 py-1.5"
          />
          <select
            name="tier"
            defaultValue={tier ?? ""}
            className="rounded border border-[var(--border)] bg-[var(--card)] px-2 py-1.5"
          >
            <option value="">全部等级</option>
            {TIERS.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <button className="rounded bg-[var(--accent)] px-3 py-1.5 text-white">筛选</button>
        </form>
      </div>

      <div className="overflow-x-auto rounded border border-[var(--border)] bg-[var(--card)]">
        <table className="w-full text-sm">
          <thead className="text-left text-[var(--muted)]">
            <tr className="border-b border-[var(--border)]">
              <th className="px-3 py-2 font-normal">客户</th>
              <th className="px-3 py-2 font-normal">城市</th>
              <th className="px-3 py-2 font-normal">等级</th>
              <th className="px-3 py-2 font-normal">风险</th>
              <th className="px-3 py-2 text-right font-normal">AUM</th>
              <th className="px-3 py-2 font-normal">客户经理</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((c) => (
              <tr key={c.id} className="border-b border-[var(--border)] last:border-0">
                <td className="px-3 py-2">
                  <Link href={`/customers/${c.id}`} className="text-[var(--accent)] hover:underline">
                    {c.name}
                  </Link>
                  <span className="ml-2 text-xs text-[var(--muted)]">{c.id}</span>
                </td>
                <td className="px-3 py-2">{c.city}</td>
                <td className="px-3 py-2">{c.tier}</td>
                <td className="px-3 py-2">{c.risk_level}</td>
                <td className="px-3 py-2 text-right tabular-nums">{formatWan(c.aum)}</td>
                <td className="px-3 py-2">{c.rm_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-end gap-3 text-sm">
        {pageNum > 1 && <Link href={href(pageNum - 1)}>上一页</Link>}
        <span className="text-[var(--muted)]">
          {pageNum} / {lastPage}
        </span>
        {pageNum < lastPage && <Link href={href(pageNum + 1)}>下一页</Link>}
      </div>
    </div>
  );
}
