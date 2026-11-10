import React from "react";
import {
  UserCheck,
  CreditCard,
  ShieldCheck,
  MailCheck,
  BarChart3,
  Settings,
  CheckCircle2,
  Clock,
  AlertCircle,
  HelpCircle,
} from "lucide-react";
import { WorkflowStep, StepStatus } from "@/types/workflow";
import { Badge } from "@/components/common/Badge";

interface NodeCardProps {
  step: WorkflowStep;
  index: number;
  totalSteps: number;
  isSelected?: boolean;
  onSelect: (step: WorkflowStep) => void;
  onConfigure: (step: WorkflowStep) => void;
  simulatedStatus?: StepStatus;
  executionDurationMs?: number;
}

export const NodeCard: React.FC<NodeCardProps> = ({
  step,
  index,
  totalSteps,
  isSelected = false,
  onSelect,
  onConfigure,
  simulatedStatus,
  executionDurationMs,
}) => {
  const getIcon = (type: string) => {
    switch (type) {
      case "registration":
        return <UserCheck className="w-5 h-5 text-indigo-400" />;
      case "payment":
        return <CreditCard className="w-5 h-5 text-sky-400" />;
      case "verification":
        return <ShieldCheck className="w-5 h-5 text-emerald-400" />;
      case "email":
        return <MailCheck className="w-5 h-5 text-violet-400" />;
      case "analytics":
        return <BarChart3 className="w-5 h-5 text-cyan-400" />;
      default:
        return <Settings className="w-5 h-5 text-slate-400" />;
    }
  };

  const status = simulatedStatus || step.status || "pending";

  const statusBadge = {
    completed: (
      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
        <CheckCircle2 className="w-3 h-3" /> Ready
      </span>
    ),
    running: (
      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-full animate-pulse">
        <Clock className="w-3 h-3 animate-spin" /> Executing
      </span>
    ),
    failed: (
      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full">
        <AlertCircle className="w-3 h-3" /> Failed
      </span>
    ),
    pending: (
      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-slate-400 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-full">
        <Clock className="w-3 h-3" /> Pending
      </span>
    ),
    skipped: (
      <span className="inline-flex items-center gap-1 text-[11px] font-mono text-slate-500 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-full">
        Skipped
      </span>
    ),
  }[status];

  return (
    <div
      onClick={() => onSelect(step)}
      className={`relative bg-slate-900/80 border rounded-2xl p-5 cursor-pointer transition-all duration-200 group ${
        isSelected
          ? "border-indigo-500 ring-2 ring-indigo-500/40 shadow-xl shadow-indigo-500/10 bg-slate-900"
          : "border-slate-800 hover:border-slate-700"
      }`}
    >
      {/* Top row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-xs font-mono font-bold text-slate-300 flex items-center justify-center">
            {index + 1}
          </span>
          <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
            {step.type}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {statusBadge}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onConfigure(step);
            }}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Configure step settings"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main icon and step info */}
      <div className="flex items-start gap-3 mb-3">
        <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 group-hover:scale-105 transition-transform">
          {getIcon(step.type)}
        </div>
        <div>
          <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
            {step.title}
          </h4>
          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2 leading-relaxed">
            {step.description}
          </p>
        </div>
      </div>

      {/* Config Highlights / Parameter preview */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
        <div>
          {step.config.capacity && (
            <span>Cap: <strong className="text-slate-200">{step.config.capacity} seats</strong></span>
          )}
          {step.config.price !== undefined && (
            <span>Fee: <strong className="text-emerald-400">${step.config.price} USD</strong></span>
          )}
          {step.config.paymentGateway && (
            <span>Provider: <strong className="text-sky-300">PayPal</strong></span>
          )}
          {step.config.emailTemplate && (
            <span>Tmpl: <strong className="text-violet-300">Auto-Pass</strong></span>
          )}
        </div>
        {executionDurationMs ? (
          <span className="text-indigo-300 font-mono">{executionDurationMs}ms</span>
        ) : step.metrics ? (
          <span>{step.metrics.avgExecutionTimeMs}ms avg</span>
        ) : null}
      </div>
    </div>
  );
};
