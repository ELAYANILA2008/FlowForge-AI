import React from "react";

export interface CardProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  headerAction?: React.ReactNode;
  className?: string;
  footer?: React.ReactNode;
  glow?: "indigo" | "emerald" | "none";
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  headerAction,
  className = "",
  footer,
  glow = "none",
}) => {
  const glowClass = {
    indigo: "glow-indigo border-indigo-500/30",
    emerald: "glow-emerald border-emerald-500/30",
    none: "border-slate-800/80",
  }[glow];

  return (
    <div
      className={`bg-slate-900/70 backdrop-blur-md rounded-xl border ${glowClass} p-5 md:p-6 transition-all duration-200 ${className}`}
    >
      {(title || headerAction) && (
        <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-800/60">
          <div>
            {typeof title === "string" ? (
              <h3 className="text-base font-semibold text-slate-100 tracking-tight">
                {title}
              </h3>
            ) : (
              title
            )}
            {subtitle && (
              <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
            )}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div>{children}</div>
      {footer && (
        <div className="mt-4 pt-3 border-t border-slate-800/60 text-xs text-slate-400">
          {footer}
        </div>
      )}
    </div>
  );
};
