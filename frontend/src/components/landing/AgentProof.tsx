import React from "react";
import Link from "next/link";
import { Gauge, CheckCircle, TrendingUp, AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/common/Badge";

export const AgentProof: React.FC = () => {
  const metrics = [
    {
      label: "Task Completion Rate",
      value: "99.4%",
      detail: "Proves agents fulfill all 5 operations without silent abandonment",
      trend: "+0.6% vs benchmark",
      color: "text-emerald-400",
    },
    {
      label: "Workflow Success Rate",
      value: "98.7%",
      detail: "End-to-end execution from intake to verified payment & ticket",
      trend: "Deterministic validation",
      color: "text-indigo-400",
    },
    {
      label: "Avg Execution Time",
      value: "1.24s",
      detail: "Ultra-low latency parallel execution mesh across all steps",
      trend: "3.2x faster than manual",
      color: "text-sky-400",
    },
    {
      label: "System Reliability Score",
      value: "99.9%",
      detail: "Built-in self-healing retry mechanisms for transient network drops",
      trend: "Zero double-charges",
      color: "text-teal-400",
    },
  ];

  return (
    <section id="performance" className="py-24 bg-surface-base relative border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-3">
            <Gauge className="w-3.5 h-3.5" />
            <span>Our Key Differentiator</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            AI Agents That Compete on Measurable Task Quality
          </h2>
          <p className="mt-3 text-slate-400 text-base">
            Most AI tools stop at generation. FlowForge continuously audits runtime execution, verifying that payments clear and emails land with mathematical precision.
          </p>
          <div className="mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-400 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            <span>Sample benchmark telemetry data (API integration ready)</span>
          </div>
        </div>

        {/* 4 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {metrics.map((m, idx) => (
            <div
              key={idx}
              className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 relative overflow-hidden"
            >
              <div className="text-xs text-slate-400 font-medium mb-1">{m.label}</div>
              <div className={`text-4xl font-extrabold tracking-tight ${m.color} mb-2 font-mono`}>
                {m.value}
              </div>
              <div className="text-xs text-slate-400 leading-relaxed mb-3">
                {m.detail}
              </div>
              <div className="pt-3 border-t border-slate-800/80 flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>{m.trend}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Benchmark Deep Dive teaser */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/30 border border-indigo-500/20 rounded-2xl p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="indigo">Deterministic Execution Guard</Badge>
              <span className="text-xs text-slate-400">Zero tolerance for hallucination in finance</span>
            </div>
            <h3 className="text-xl font-bold text-white">
              Every step is validated with cryptographic receipts & error recovery
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              If an email fails to deliver or PayPal experiences a webhook timeout, our automated recovery agents retry and report back to your owner dashboard immediately.
            </p>
          </div>
          <Link
            href="/dashboard/performance"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium border border-slate-700 transition-colors whitespace-nowrap"
          >
            <span>View Full Agent Benchmark</span>
            <ArrowRight className="w-4 h-4 text-indigo-400" />
          </Link>
        </div>
      </div>
    </section>
  );
};
