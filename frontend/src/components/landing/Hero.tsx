"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Sparkles, ShieldCheck, PlayCircle, Layers, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/common/Button";

interface HeroProps {
  onOpenDemo?: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onOpenDemo }) => {
  return (
    <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-600/15 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[250px] bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Top badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 border border-indigo-500/30 text-xs font-medium text-indigo-300 mb-8 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Next-Gen Autonomous Business Workflows</span>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
          <span className="text-slate-400 font-mono">99.4% Verifiable Task Quality</span>
        </div>

        {/* Main headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1]">
          Turn Ideas Into{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-300 to-cyan-400 bg-clip-text text-transparent">
            Automated Business Operations.
          </span>
        </h1>

        {/* Supporting description */}
        <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
          State your business goal in plain English. FlowForge AI synthesizes your customer registration portal, integrates PayPal checkouts, verifies transactions, sends tickets, and streams live telemetry.
        </p>

        {/* Action CTAs */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/dashboard/builder">
            <Button
              size="lg"
              variant="primary"
              className="w-full sm:w-auto text-base px-8 py-3.5 font-semibold"
              rightIcon={<ArrowRight className="w-4 h-4 ml-1" />}
            >
              Build Your First Workflow
            </Button>
          </Link>
          <button
            onClick={() => {
              const el = document.getElementById("visualizer");
              el?.scrollIntoView({ behavior: "smooth" });
              if (onOpenDemo) onOpenDemo();
            }}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg text-slate-200 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 font-medium text-sm transition-colors hover:text-white"
          >
            <PlayCircle className="w-4 h-4 text-indigo-400" />
            Explore Demo Pipeline
          </button>
        </div>

        {/* Key Guarantees */}
        <div className="mt-12 pt-8 border-t border-slate-800/60 max-w-3xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="text-xs text-slate-300">Natural-Language Synthesis</span>
          </div>
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="text-xs text-slate-300">PayPal Webhook Verification</span>
          </div>
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="text-xs text-slate-300">Automated Ticket Dispatch</span>
          </div>
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="text-xs text-slate-300">Auditable Quality Metrics</span>
          </div>
        </div>
      </div>
    </section>
  );
};
