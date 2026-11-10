import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatWan, listCustomers } from "@/lib/api";
import { cn } from "@/lib/utils";

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
        <h1 className="text-xl font-semibold">
          客户 <span className="text-muted-foreground font-normal">{data.total}</span>
        </h1>
        <form className="flex flex-wrap gap-2">
          <Input name="q" defaultValue={q} placeholder="姓名或客户 ID" className="w-44" />
          <select
            name="tier"
            defaultValue={tier ?? ""}
            className="h-8 rounded-lg border border-input bg-transparent px-2 text-sm"
          >
            <option value="">全部等级</option>
            {TIERS.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <Button type="submit">筛选</Button>
        </form>
      </div>

      <Card className="py-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>客户</TableHead>
              <TableHead>城市</TableHead>
              <TableHead>等级</TableHead>
              <TableHead>风险</TableHead>
              <TableHead className="text-right">AUM</TableHead>
              <TableHead>客户经理</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.items.map((c) => (
              <TableRow key={c.id}>
                <TableCell>
                  <Link href={`/customers/${c.id}`} className="text-primary hover:underline">
                    {c.name}
                  </Link>
                  <span className="text-muted-foreground ml-2 text-xs">{c.id}</span>
                </TableCell>
                <TableCell>{c.city}</TableCell>
                <TableCell>
                  <Badge variant={c.tier === "钻石" || c.tier === "铂金" ? "default" : "secondary"}>
                    {c.tier}
                  </Badge>
                </TableCell>
                <TableCell>{c.risk_level}</TableCell>
                <TableCell className="text-right tabular-nums">{formatWan(c.aum)}</TableCell>
                <TableCell>{c.rm_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <div className="flex items-center justify-end gap-2 text-sm">
        {pageNum > 1 && (
          <Link href={href(pageNum - 1)} className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
            上一页
          </Link>
        )}
        <span className="text-muted-foreground px-2">
          {pageNum} / {lastPage}
        </span>
        {pageNum < lastPage && (
          <Link href={href(pageNum + 1)} className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
            下一页
          </Link>
        )}
      </div>
    </div>
  );
}
