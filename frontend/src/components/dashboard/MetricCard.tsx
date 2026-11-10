import React from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

export interface MetricCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon: React.ReactNode;
  color?: "indigo" | "emerald" | "rose" | "cyan" | "amber";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  change,
  trend = "up",
  icon,
  color = "indigo",
}) => {
  const colorMap = {
    indigo: "border-indigo-500/20 text-indigo-400 bg-indigo-500/10",
    emerald: "border-emerald-500/20 text-emerald-400 bg-emerald-500/10",
    rose: "border-rose-500/20 text-rose-400 bg-rose-500/10",
    cyan: "border-cyan-500/20 text-cyan-400 bg-cyan-500/10",
    amber: "border-amber-500/20 text-amber-400 bg-amber-500/10",
  }[color];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        <div className={`p-2 rounded-lg border ${colorMap}`}>{icon}</div>
      </div>

      <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight mb-1">
        {value}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{subtitle}</span>
        {change && (
          <span
            className={`inline-flex items-center gap-1 font-medium font-mono text-[11px] ${
              trend === "up"
                ? "text-emerald-400"
                : trend === "down"
                ? "text-rose-400"
                : "text-slate-400"
            }`}
          >
            {trend === "up" && <TrendingUp className="w-3 h-3" />}
            {trend === "down" && <TrendingDown className="w-3 h-3" />}
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
