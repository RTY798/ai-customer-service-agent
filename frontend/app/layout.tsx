import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "电商智能客服系统",
  description: "基于 LangGraph 的多 Agent 电商智能客服系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
