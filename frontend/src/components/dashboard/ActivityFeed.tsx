import React from "react";
import Link from "next/link";
import { CreditCard, MailCheck, UserCheck, AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import { ActivityFeedItem } from "@/types/metrics";

interface ActivityFeedProps {
  items: ActivityFeedItem[];
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ items }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case "payment":
        return <CreditCard className="w-4 h-4 text-emerald-400" />;
      case "email":
        return <MailCheck className="w-4 h-4 text-violet-400" />;
      case "registration":
        return <UserCheck className="w-4 h-4 text-indigo-400" />;
      case "error":
        return <AlertTriangle className="w-4 h-4 text-rose-400" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-sky-400" />;
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-sm font-semibold text-white">Live Activity Stream</h3>
          <p className="text-xs text-slate-400">Verifiable operational events as they execute</p>
        </div>
        <span className="inline-flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Live Listening
        </span>
      </div>

      <div className="space-y-3.5">
        {items.map((item) => (
          <div
            key={item.id}
            className="flex items-start justify-between gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 mt-0.5">
                {getIcon(item.type)}
              </div>
              <div>
                <div className="text-xs font-semibold text-white flex items-center gap-2">
                  <span>{item.title}</span>
                  {item.amount && (
                    <span className="text-[11px] font-mono text-emerald-400 font-bold">
                      +${item.amount.toFixed(2)}
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-400 mt-0.5 leading-snug">
                  {item.description}
                </div>
                <div className="text-[10px] text-slate-400 mt-1 font-mono">
                  {item.workflowTitle}
                </div>
              </div>
            </div>
            <span className="text-[10px] text-slate-400 whitespace-nowrap font-mono">
              {item.timestamp}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 text-center">
        <Link
          href="/dashboard/workflows"
          className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
        >
          View all workflow audit logs <ArrowRight className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
};
