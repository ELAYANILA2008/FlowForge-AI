import React from "react";

export type BadgeVariant =
  | "active"
  | "completed"
  | "paused"
  | "failed"
  | "pending"
  | "optimal"
  | "indigo"
  | "neutral";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: "sm" | "md";
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  size = "md",
  dot = false,
  className = "",
}) => {
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs font-medium",
    md: "px-2.5 py-1 text-xs font-semibold",
  }[size];

  const variantClasses: Record<BadgeVariant, { badge: string; dot: string }> = {
    active: {
      badge: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
      dot: "bg-emerald-400",
    },
    completed: {
      badge: "bg-teal-500/10 text-teal-400 border border-teal-500/30",
      dot: "bg-teal-400",
    },
    paused: {
      badge: "bg-amber-500/10 text-amber-400 border border-amber-500/30",
      dot: "bg-amber-400",
    },
    failed: {
      badge: "bg-rose-500/10 text-rose-400 border border-rose-500/30",
      dot: "bg-rose-400",
    },
    pending: {
      badge: "bg-sky-500/10 text-sky-400 border border-sky-500/30",
      dot: "bg-sky-400",
    },
    optimal: {
      badge: "bg-indigo-500/10 text-indigo-400 border border-indigo-500/30",
      dot: "bg-indigo-400",
    },
    indigo: {
      badge: "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30",
      dot: "bg-indigo-400",
    },
    neutral: {
      badge: "bg-slate-800 text-slate-300 border border-slate-700/60",
      dot: "bg-slate-400",
    },
  };

  const current = variantClasses[variant] || variantClasses.neutral;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full ${sizeClasses} ${current.badge} ${className}`}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${current.dot}`} />
      )}
      {children}
    </span>
  );
};
