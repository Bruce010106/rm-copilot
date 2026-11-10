import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatWan, getCustomer } from "@/lib/api";

export default async function CustomerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = await getCustomer(id);
  if (!c) notFound();

  const age = new Date().getFullYear() - Number(c.birth_date.slice(0, 4));
  const facts: [string, string][] = [
    ["AUM", formatWan(c.aum)],
    ["风险等级", c.risk_level],
    ["城市", c.city],
    ["职业", c.occupation],
    ["年龄", `${age}`],
    ["客户经理", c.rm_name],
    ["开户", c.onboarded_at],
    ["持仓数", `${c.holdings.length}`],
  ];

  return (
    <div className="space-y-6">
      <div>
        <Link href="/customers" className="text-muted-foreground text-sm hover:text-foreground">
          ← 客户列表
        </Link>
        <h1 className="mt-1 flex items-center gap-2 text-xl font-semibold">
          {c.name}
          <Badge>{c.tier}</Badge>
          <span className="text-muted-foreground text-sm font-normal">{c.id}</span>
        </h1>
      </div>

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {facts.map(([k, v]) => (
          <Card key={k} size="sm" className="gap-1">
            <CardContent>
              <div className="text-muted-foreground text-xs">{k}</div>
              <div className="mt-1 font-medium">{v}</div>
            </CardContent>
          </Card>
        ))}
      </section>

      <Card className="border-dashed bg-transparent shadow-none ring-0">
        <CardContent className="text-muted-foreground text-sm">
          AI 摘要（带证据引用）开发中，见 Issue #2。
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>持仓</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-y text-sm">
              {c.holdings.map((h) => (
                <li key={h.id} className="flex justify-between gap-3 py-2">
                  <div>
                    <div>{h.product_name}</div>
                    <div className="text-muted-foreground text-xs">
                      {h.category}
                      {h.maturity_date && ` · 到期 ${h.maturity_date}`}
                    </div>
                  </div>
                  <div className="tabular-nums">{formatWan(h.amount)}</div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>服务记录</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3 text-sm">
              {c.interactions.map((i) => (
                <li key={i.id} className="border-l-2 pl-3">
                  <div className="text-muted-foreground text-xs">
                    {i.occurred_at.replace("T", " ").slice(0, 16)} · {i.channel} · {i.id}
                  </div>
                  <div className="mt-0.5">{i.content}</div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
