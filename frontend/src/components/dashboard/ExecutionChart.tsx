"use client";

import React, { useState } from "react";
import { BarChart3, TrendingUp } from "lucide-react";

interface ExecutionChartProps {
  revenueTrend: { date: string; amount: number; registrations: number }[];
  executionTrend: { date: string; successful: number; failed: number }[];
}

export const ExecutionChart: React.FC<ExecutionChartProps> = ({
  revenueTrend,
  executionTrend,
}) => {
  const [activeTab, setActiveTab] = useState<"revenue" | "executions">("revenue");

  const maxRevenue = Math.max(...revenueTrend.map((d) => d.amount), 3000);
  const maxExecutions = Math.max(...executionTrend.map((d) => d.successful + d.failed), 140);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            Execution & Revenue Telemetry
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Operational throughput and volume across the last 7 calendar days
          </p>
        </div>

        <div className="flex items-center gap-1 p-1 bg-slate-950 border border-slate-800 rounded-lg text-xs">
          <button
            onClick={() => setActiveTab("revenue")}
            className={`px-3 py-1 rounded-md font-medium transition-colors ${
              activeTab === "revenue"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Revenue Volume ($)
          </button>
          <button
            onClick={() => setActiveTab("executions")}
            className={`px-3 py-1 rounded-md font-medium transition-colors ${
              activeTab === "executions"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Task Executions
          </button>
        </div>
      </div>

      {activeTab === "revenue" ? (
        <div>
          <div className="h-56 flex items-end justify-between gap-2 pt-6">
            {revenueTrend.map((item, idx) => {
              const heightPct = Math.round((item.amount / maxRevenue) * 100);
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                  {/* Tooltip on hover */}
                  <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-700 text-white text-[11px] font-mono px-2 py-1 rounded shadow-lg pointer-events-none whitespace-nowrap z-20">
                    ${item.amount} ({item.registrations} regs)
                  </div>

                  <div className="w-full bg-slate-800/80 rounded-t-md h-full flex items-end overflow-hidden">
                    <div
                      className="w-full bg-gradient-to-t from-indigo-700 to-indigo-500 rounded-t-md transition-all duration-500 group-hover:from-indigo-600 group-hover:to-indigo-400"
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{item.date}</span>
                </div>
              );
            })}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Peak: <strong className="text-slate-200">$2,680.00 / day</strong></span>
            <span className="text-emerald-400 flex items-center gap-1 font-mono">
              <TrendingUp className="w-3.5 h-3.5" /> +24.8% weekly gain
            </span>
          </div>
        </div>
      ) : (
        <div>
          <div className="h-56 flex items-end justify-between gap-2 pt-6">
            {executionTrend.map((item, idx) => {
              const total = item.successful + item.failed;
              const heightPct = Math.round((total / maxExecutions) * 100);
              const failPct = total > 0 ? (item.failed / total) * 100 : 0;

              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                  {/* Tooltip */}
                  <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-700 text-white text-[11px] font-mono px-2 py-1 rounded shadow-lg pointer-events-none whitespace-nowrap z-20">
                    {item.successful} ok · {item.failed} failed
                  </div>

                  <div className="w-full bg-slate-800/80 rounded-t-md h-full flex items-end overflow-hidden">
                    <div
                      className="w-full bg-emerald-500/80 rounded-t-md flex flex-col justify-end transition-all duration-500"
                      style={{ height: `${heightPct}%` }}
                    >
                      {item.failed > 0 && (
                        <div
                          className="w-full bg-rose-500"
                          style={{ height: `${failPct}%` }}
                        />
                      )}
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{item.date}</span>
                </div>
              );
            })}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                Successful (99.2%)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                Failed (0.8%)
              </span>
            </div>
            <span className="text-slate-400 font-mono">688 Total Runs</span>
          </div>
        </div>
      )}
    </div>
  );
};
