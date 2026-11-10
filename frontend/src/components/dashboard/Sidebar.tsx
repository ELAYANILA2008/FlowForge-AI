"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Sparkles,
  Layers,
  Gauge,
  ExternalLink,
  ChevronLeft,
  Cpu,
  X,
} from "lucide-react";

interface SidebarProps {
  onCloseMobile?: () => void;
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile, className = "" }) => {
  const pathname = usePathname();

  const navigation = [
    {
      name: "Dashboard Overview",
      href: "/dashboard",
      icon: LayoutDashboard,
      current: pathname === "/dashboard",
    },
    {
      name: "AI Workflow Builder",
      href: "/dashboard/builder",
      icon: Sparkles,
      current: pathname === "/dashboard/builder",
      badge: "Core AI",
    },
    {
      name: "Workflows",
      href: "/dashboard/workflows",
      icon: Layers,
      current: pathname.startsWith("/dashboard/workflows"),
    },
    {
      name: "Agent Performance",
      href: "/dashboard/performance",
      icon: Gauge,
      current: pathname === "/dashboard/performance",
      badge: "99.4%",
    },
  ];

  return (
    <aside
      className={`w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0 ${className}`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 px-6 border-b border-slate-800/80 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5" onClick={onCloseMobile}>
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30">
              <Cpu className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-white flex items-center gap-1">
                FlowForge <span className="text-indigo-400">AI</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Console v0.1</span>
            </div>
          </Link>

          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="p-1 rounded-lg text-slate-400 hover:text-white md:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation list */}
        <div className="px-3 py-6 space-y-1">
          <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Operations
          </div>
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={onCloseMobile}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  item.current
                    ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={`w-4 h-4 ${
                      item.current ? "text-indigo-400" : "text-slate-400"
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      item.current
                        ? "bg-indigo-500/20 text-indigo-300"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}

          <div className="pt-6 px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Customer Surface
          </div>
          <Link
            href="/preview/wf-photo-001"
            onClick={onCloseMobile}
            className="flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <ExternalLink className="w-4 h-4 text-emerald-400" />
              <span>Registration Preview</span>
            </div>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded font-mono">
              Live
            </span>
          </Link>
        </div>
      </div>

      {/* Footer / System Status */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-300">Agent Quality</span>
            <span className="text-[11px] font-mono text-emerald-400 font-bold">99.4%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-400 rounded-full" style={{ width: "99.4%" }} />
          </div>
          <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
            <span>524 tasks verified</span>
            <span className="text-emerald-400">Zero fraud</span>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-slate-400 px-1">
          <Link
            href="/"
            onClick={onCloseMobile}
            className="hover:text-slate-300 transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" /> Back to Home
          </Link>
          <span className="text-[10px] text-slate-400 font-mono">Alpha v0.1</span>
        </div>
      </div>
    </aside>
  );
};
