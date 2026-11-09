import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "RM Copilot",
  description: "AI workspace for relationship managers",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">
        <header className="border-b border-[var(--border)] bg-[var(--card)]">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 text-sm">
            <Link href="/" className="font-semibold text-[var(--accent)]">
              RM Copilot
            </Link>
            <Link href="/customers">客户</Link>
            <span className="text-[var(--muted)]">今日工作（W6）</span>
            <span className="text-[var(--muted)]">问数（W4）</span>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
