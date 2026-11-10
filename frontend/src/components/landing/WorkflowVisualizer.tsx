"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  UserCheck,
  CreditCard,
  ShieldCheck,
  MailCheck,
  BarChart3,
  ArrowRight,
  Play,
  RotateCcw,
  Check,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/common/Button";

interface StepPreview {
  id: string;
  name: string;
  type: string;
  icon: React.ReactNode;
  summary: string;
  metric: string;
  detail: {
    title: string;
    description: string;
    configKey: string;
    configValue: string;
  };
}

const DEMO_STEPS: StepPreview[] = [
  {
    id: "step-1",
    name: "Registration",
    type: "Customer Portal",
    icon: <UserCheck className="w-5 h-5 text-indigo-400" />,
    summary: "50 Seats Limit",
    metric: "140ms latency",
    detail: {
      title: "Student Registration Portal",
      description: "Auto-generates hosted customer intake form with live concurrency lock preventing over-subscription.",
      configKey: "Max Capacity",
      configValue: "50 Attendees (16 left)",
    },
  },
  {
    id: "step-2",
    name: "Payment",
    type: "PayPal Gateway",
    icon: <CreditCard className="w-5 h-5 text-sky-400" />,
    summary: "$20.00 / student",
    metric: "420ms latency",
    detail: {
      title: "PayPal Modal Checkout",
      description: "Directs students through instant PayPal sandbox or live checkout with zero code integration.",
      configKey: "Transaction Fee",
      configValue: "$20.00 USD (Fixed)",
    },
  },
  {
    id: "step-3",
    name: "Verification",
    type: "Fraud & Webhook",
    icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
    summary: "100% Cryptographic",
    metric: "190ms latency",
    detail: {
      title: "IPN / Webhook Cryptographic Verification",
      description: "Verifies PayPal payload signatures, detects double-spending, and checks merchant account credit.",
      configKey: "Risk Validation",
      configValue: "Deterministic Signature Guard",
    },
  },
  {
    id: "step-4",
    name: "Confirmation",
    type: "Transactional Email",
    icon: <MailCheck className="w-5 h-5 text-violet-400" />,
    summary: "Ticket & Calendar",
    metric: "310ms latency",
    detail: {
      title: "Automated Ticket Dispatch",
      description: "Compiles personalized attendee admission badge with QR code and adds calendar (.ics) invite.",
      configKey: "Delivery Route",
      configValue: "Instant SMTP / Resend Mesh",
    },
  },
  {
    id: "step-5",
    name: "Dashboard",
    type: "Business Telemetry",
    icon: <BarChart3 className="w-5 h-5 text-cyan-400" />,
    summary: "Realtime Analytics",
    metric: "110ms latency",
    detail: {
      title: "Business Operator Telemetry",
      description: "Syncs seat counter, increments revenue telemetry (+$20), and logs transaction for owner audit.",
      configKey: "Metrics State",
      configValue: "34/50 Claimed · $680.00 Raised",
    },
  },
];

export const WorkflowVisualizer: React.FC = () => {
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [simulating, setSimulating] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  const runSimulation = () => {
    if (simulating) return;
    setSimulating(true);
    setCompletedSteps([]);
    setActiveStepIndex(0);

    DEMO_STEPS.forEach((_, idx) => {
      setTimeout(() => {
        setActiveStepIndex(idx);
        setCompletedSteps((prev) => [...prev, idx]);
        if (idx === DEMO_STEPS.length - 1) {
          setSimulating(false);
        }
      }, (idx + 1) * 700);
    });
  };

  const activeStep = DEMO_STEPS[activeStepIndex];

  return (
    <section id="visualizer" className="py-20 bg-slate-950/60 border-y border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interactive Workflow Engine</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            How FlowForge AI Chains Your Entire Business
          </h2>
          <p className="mt-3 text-slate-300 text-sm sm:text-base">
            From a single natural-language instruction, AI synthesizes a production-grade operations pipeline with verifiable checkpoints.
          </p>
        </div>

        {/* Prompt Card Preview */}
        <div className="max-w-4xl mx-auto bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-6 mb-10 shadow-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">
                Natural-Language Prompt Input
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={runSimulation}
                disabled={simulating}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors disabled:opacity-50"
              >
                {simulating ? (
                  <>
                    <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                    Simulating Run...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    Simulate Pipeline Execution
                  </>
                )}
              </button>
              <Link href="/preview/wf-photo-001">
                <Button variant="outline" size="sm" rightIcon={<ExternalLink className="w-3 h-3" />}>
                  Live Preview
                </Button>
              </Link>
            </div>
          </div>
          <div className="mt-4 p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-sm text-indigo-300">
            &quot;Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails.&quot;
          </div>
        </div>

        {/* Connected Node Visualizer */}
        <div className="max-w-5xl mx-auto">
          {/* Steps Timeline Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 relative">
            {DEMO_STEPS.map((step, idx) => {
              const isActive = activeStepIndex === idx;
              const isDone = completedSteps.includes(idx);

              return (
                <div
                  key={step.id}
                  onClick={() => setActiveStepIndex(idx)}
                  className={`cursor-pointer rounded-xl p-4 transition-all duration-200 border relative ${
                    isActive
                      ? "bg-slate-800/90 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500/50"
                      : isDone
                      ? "bg-slate-900/80 border-emerald-500/40 hover:border-emerald-500/80"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {/* Step number badge */}
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-bold font-mono ${
                        isDone
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                          : isActive
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {isDone ? <Check className="w-3.5 h-3.5" /> : idx + 1}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">{step.metric}</span>
                  </div>

                  <div className="mb-2">{step.icon}</div>
                  <div className="font-semibold text-sm text-white mb-0.5">{step.name}</div>
                  <div className="text-xs text-slate-400 truncate">{step.summary}</div>

                  {isActive && (
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-slate-800 border-r border-b border-indigo-500 rotate-45 hidden sm:block" />
                  )}
                </div>
              );
            })}
          </div>

          {/* Active Step Deep Dive Panel */}
          <div className="mt-6 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700">
                  {activeStep.icon}
                </div>
                <div>
                  <div className="text-xs font-mono uppercase tracking-wider text-indigo-400">
                    Step {activeStepIndex + 1} of 5 · {activeStep.type}
                  </div>
                  <h3 className="text-lg font-bold text-white mt-0.5">
                    {activeStep.detail.title}
                  </h3>
                </div>
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono">
                <span className="text-slate-400">{activeStep.detail.configKey}:</span>
                <span className="text-emerald-400 font-medium">{activeStep.detail.configValue}</span>
              </div>
            </div>

            <p className="mt-4 text-sm text-slate-300 leading-relaxed">
              {activeStep.detail.description}
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
              <div className="flex items-center gap-4">
                <span>Fault Tolerance: <strong className="text-slate-200">Auto-Retry Enabled</strong></span>
                <span>Audit Trail: <strong className="text-slate-200">Cryptographically Signed</strong></span>
              </div>
              <Link
                href="/dashboard/builder"
                className="inline-flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
              >
                Inspect in Workflow Builder <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
