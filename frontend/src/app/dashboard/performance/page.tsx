"use client";

import React, { useState, useEffect } from "react";
import {
  Gauge,
  CheckCircle2,
  Clock,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Cpu,
  Layers,
  ArrowRight,
  Info,
} from "lucide-react";
import { TopNav } from "@/components/dashboard/TopNav";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { Badge } from "@/components/common/Badge";
import { MetricsService } from "@/services/api";
import { AgentPerformanceMetric } from "@/types/metrics";

export default function AgentPerformancePage() {
  const [agents, setAgents] = useState<AgentPerformanceMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await MetricsService.getAgentPerformance();
        setAgents(data);
      } catch (err) {
        console.error("Failed to load agent benchmarks", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <TopNav
        title="AI Agent Performance & Quality Benchmarks"
        subtitle="Verifiable task completion, deterministic reliability, and latency telemetry"
      />

      <main className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full flex-1">
        {/* Sample Telemetry Disclaimer Banner (Required by prompt) */}
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-start gap-3">
          <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-indigo-200 leading-relaxed">
            <strong className="text-white font-semibold">Demonstration Benchmark Data:</strong>{" "}
            The indicators below reflect simulated benchmark runs under load. When the live FastAPI backend is connected, this dashboard will stream real-time telemetry directly from production audit nodes.
          </div>
        </div>

        {/* 4 Core Differentiation KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Overall Task Completion"
            value="99.4%"
            subtitle="Zero silent agent drops"
            change="+0.6% vs target"
            icon={<CheckCircle2 className="w-4 h-4" />}
            color="emerald"
          />
          <MetricCard
            label="Workflow Success Rate"
            value="98.7%"
            subtitle="Complete operational fulfillment"
            change="Deterministic verification"
            icon={<ShieldCheck className="w-4 h-4" />}
            color="indigo"
          />
          <MetricCard
            label="Average Latency"
            value="1.24s"
            subtitle="Full multi-step execution"
            change="3.4x faster"
            icon={<Clock className="w-4 h-4" />}
            color="cyan"
          />
          <MetricCard
            label="System Reliability Score"
            value="99.9%"
            subtitle="Self-healing auto retries"
            change="0 double-charges"
            icon={<Gauge className="w-4 h-4" />}
            color="emerald"
          />
        </div>

        {/* Agent Comparison Matrix */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                Autonomous Agent Roster & Benchmark Comparison
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Each operational agent is evaluated on deterministic execution, error recovery, and latency
              </p>
            </div>
            <Badge variant="optimal">Deterministic Guard v2</Badge>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Agent Name & Role</th>
                  <th className="pb-3 font-semibold">Underlying Architecture</th>
                  <th className="pb-3 font-semibold">Completion Rate</th>
                  <th className="pb-3 font-semibold">Success Rate</th>
                  <th className="pb-3 font-semibold">Avg Latency</th>
                  <th className="pb-3 font-semibold">Self-Healing Recovery</th>
                  <th className="pb-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {agents.map((agent) => (
                  <tr key={agent.id} className="hover:bg-slate-950/40 transition-colors">
                    <td className="py-4 pr-4">
                      <div className="font-sans font-bold text-white text-sm">
                        {agent.name}
                      </div>
                      <div className="font-sans text-[11px] text-slate-400 mt-0.5">
                        {agent.role}
                      </div>
                    </td>
                    <td className="py-4 pr-4 text-slate-300">
                      <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[11px]">
                        {agent.model}
                      </span>
                    </td>
                    <td className="py-4 pr-4">
                      <span className="font-bold text-emerald-400">
                        {agent.taskCompletionRate}%
                      </span>
                      <div className="text-[10px] text-slate-500 font-sans">
                        {agent.totalTasksProcessed - agent.failedTaskCount} / {agent.totalTasksProcessed}
                      </div>
                    </td>
                    <td className="py-4 pr-4 font-bold text-slate-200">
                      {agent.workflowSuccessRate}%
                    </td>
                    <td className="py-4 pr-4 text-indigo-300">
                      {agent.avgExecutionTimeMs}ms
                    </td>
                    <td className="py-4 pr-4 text-teal-300">
                      {agent.recoveryRate}%
                    </td>
                    <td className="py-4">
                      <Badge variant="active" size="sm" dot>
                        OPTIMAL
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quality Audit Explanation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              How Task Quality Is Measured
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Unlike chatbots where responses are subjective, FlowForge AI measures binary transactional outcomes: Did the student get registered? Did the PayPal order settle? Did the verification pass cryptographically? Did the calendar confirmation reach the student&apos;s inbox?
            </p>
            <div className="text-[11px] text-slate-400 font-mono pt-2 border-t border-slate-800">
              Audit Standard: RFC-7519 Cryptographic Claims with IPN Double-Entry Logging.
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Self-Healing & Fault Tolerance
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              In real-world business operations, network drops and third-party API throttling occur. FlowForge includes automated retry loops with exponential backoff and circuit breakers, ensuring zero dropped payments or duplicate charges.
            </p>
            <div className="text-[11px] text-slate-400 font-mono pt-2 border-t border-slate-800">
              Recovery Performance: 98.2% automated fault resolution without operator intervention.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
