"use client";

import React from "react";
import Link from "next/link";
import { Sparkles, Plus, Menu } from "lucide-react";
import { Button } from "@/components/common/Button";

interface TopNavProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  onOpenMobileMenu?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  title,
  subtitle,
  actions,
  onOpenMobileMenu,
}) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <div>
          {title && (
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center gap-2">
              {title}
            </h1>
          )}
          {subtitle && <p className="text-xs text-slate-400 hidden sm:block">{subtitle}</p>}
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Mock Data Banner Badge */}
        <div className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] font-mono text-indigo-300">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Demo Data Mode (FastAPI Contract Ready)</span>
        </div>

        {actions}

        <Link href="/dashboard/builder">
          <Button
            size="sm"
            variant="primary"
            leftIcon={<Plus className="w-3.5 h-3.5" />}
          >
            <span className="hidden sm:inline">New Workflow</span>
            <span className="sm:hidden">New</span>
          </Button>
        </Link>

        {/* User avatar mockup */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-xs font-bold text-white shadow-sm ring-1 ring-slate-700">
          FF
        </div>
      </div>
    </header>
  );
};
