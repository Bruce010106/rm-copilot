import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "RM Copilot",
  description: "AI workspace for relationship managers",
};

const NAV = [
  { href: "/customers", label: "客户", ready: true },
  { href: "#", label: "今日工作", ready: false },
  { href: "#", label: "问数", ready: false },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">
        <header className="border-b bg-card">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 text-sm">
            <Link href="/" className="font-semibold text-primary">
              RM Copilot
            </Link>
            {NAV.map((item) =>
              item.ready ? (
                <Link key={item.label} href={item.href} className="hover:text-primary">
                  {item.label}
                </Link>
              ) : (
                <span key={item.label} className="text-muted-foreground" title="开发中">
                  {item.label}
                </span>
              ),
            )}
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
