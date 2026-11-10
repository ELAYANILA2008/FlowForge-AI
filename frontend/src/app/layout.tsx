import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FlowForge AI | AI That Builds & Runs Business Operations Automatically",
  description:
    "Transform plain English instructions into self-operating, self-monitoring business workflows with built-in registration, PayPal payments, and verifiable execution metrics.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="min-h-screen bg-surface-base text-slate-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
        {children}
      </body>
    </html>
  );
}
