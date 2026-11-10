import React from "react";
import { MessageSquareText, Cpu, CheckCircle, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/common/Button";

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      num: "01",
      icon: <MessageSquareText className="w-6 h-6 text-indigo-400" />,
      title: "1. Prompt Your Business Goal",
      description:
        "Type your instruction in plain English: 'Organize a photography workshop for 50 students at $20 each with PayPal and email tickets.'",
      badge: "Prompt Understanding",
    },
    {
      num: "02",
      icon: <Cpu className="w-6 h-6 text-sky-400" />,
      title: "2. AI Synthesizes Pipeline",
      description:
        "FlowForge creates the customer registration portal, configures PayPal checkout parameters, sets up IPN verification, and designs email templates.",
      badge: "Automated Assembly",
    },
    {
      num: "03",
      icon: <CheckCircle className="w-6 h-6 text-emerald-400" />,
      title: "3. Run & Monitor Autonomously",
      description:
        "Students register, payments clear into your PayPal account, confirmation tickets dispatch instantly, and your dashboard updates in real time.",
      badge: "Measurable Quality",
    },
  ];

  return (
    <section id="how-it-works" className="py-24 bg-slate-950 border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 mb-3">
            <span>Execution Workflow</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            From Natural Language to Running Operations in Seconds
          </h2>
          <p className="mt-3 text-slate-400 text-base">
            No complex zap configurations or fragile webhook glue code. Let AI assemble and govern the entire flow.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {steps.map((s, idx) => (
            <div
              key={idx}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-7 relative flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
                    {s.icon}
                  </div>
                  <span className="text-2xl font-black font-mono text-slate-700">
                    {s.num}
                  </span>
                </div>
                <div className="inline-block px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-xs font-mono font-medium text-indigo-400 mb-3">
                  {s.badge}
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{s.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  {s.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 text-center">
          <Link href="/dashboard/builder">
            <Button size="lg" variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
              Try Workflow Builder Now
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
};
