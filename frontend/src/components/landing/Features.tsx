import React from "react";
import {
  Wand2,
  CreditCard,
  ShieldCheck,
  MailCheck,
  BarChart4,
  Layers,
  Zap,
  Gauge,
  Lock,
} from "lucide-react";

const FEATURES = [
  {
    icon: <Wand2 className="w-6 h-6 text-indigo-400" />,
    title: "Natural-Language Workflow Engine",
    description:
      "Simply state what your business needs to accomplish. FlowForge interprets parameters, constraints, and dependencies automatically.",
  },
  {
    icon: <Layers className="w-6 h-6 text-sky-400" />,
    title: "Instant Customer Intake Portals",
    description:
      "Generates polished, responsive registration pages with live capacity management, custom fields, and real-time seat decrementing.",
  },
  {
    icon: <CreditCard className="w-6 h-6 text-emerald-400" />,
    title: "PayPal Gateway & Checkout",
    description:
      "Seamless integration with PayPal sandbox and production checkouts. Accepts payments with zero backend code required.",
  },
  {
    icon: <ShieldCheck className="w-6 h-6 text-amber-400" />,
    title: "Cryptographic Payment Verification",
    description:
      "Verifies webhook IPNs, validates fraud signatures, and ensures tickets are dispatched only after funds are captured.",
  },
  {
    icon: <MailCheck className="w-6 h-6 text-violet-400" />,
    title: "Automated Ticket & Calendar Dispatch",
    description:
      "Sends branded confirmation emails, PDF entry passes with QR codes, and calendar invitations with 99.5% delivery rates.",
  },
  {
    icon: <Gauge className="w-6 h-6 text-cyan-400" />,
    title: "Verifiable Agent Quality Telemetry",
    description:
      "FlowForge AI agents compete on measurable task completion, reliability scores, and deterministic execution latencies.",
  },
];

export const Features: React.FC = () => {
  return (
    <section id="features" className="py-24 bg-surface-base relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 mb-3">
            <Zap className="w-3.5 h-3.5 text-indigo-400" />
            <span>Platform Capabilities</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Everything Required to Operate Your Business Autonomously
          </h2>
          <p className="mt-3 text-slate-400 text-base">
            Not just a landing page builder. FlowForge AI coordinates the end-to-end operational lifecycle from registration to fulfillment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((feat, idx) => (
            <div
              key={idx}
              className="bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/40 rounded-2xl p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-500/5 group"
            >
              <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center mb-5 group-hover:scale-105 group-hover:bg-slate-800 transition-all">
                {feat.icon}
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {feat.title}
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                {feat.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
