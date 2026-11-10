"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  CheckCircle2,
  Clock,
  AlertCircle,
  X,
  ExternalLink,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import { Workflow, WorkflowStep } from "@/types/workflow";
import { Button } from "@/components/common/Button";
import Link from "next/link";

interface RunSimulationModalProps {
  workflow: Workflow;
  isOpen: boolean;
  onClose: () => void;
  onSimulationComplete?: () => void;
}

export const RunSimulationModal: React.FC<RunSimulationModalProps> = ({
  workflow,
  isOpen,
  onClose,
  onSimulationComplete,
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [stepLogs, setStepLogs] = useState<{ stepId: string; title: string; status: "success" | "running"; durationMs: number; message: string }[]>([]);
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    if (isOpen) {
      resetAndRun();
    }
  }, [isOpen]);

  const resetAndRun = () => {
    setIsRunning(true);
    setIsFinished(false);
    setCurrentStepIndex(0);
    setStepLogs([]);

    const steps = workflow.steps;
    let accumulatedTime = 0;

    steps.forEach((step, idx) => {
      const stepDuration = 500 + idx * 250;
      accumulatedTime += stepDuration;

      setTimeout(() => {
        setCurrentStepIndex(idx);
        setStepLogs((prev) => [
          ...prev,
          {
            stepId: step.id,
            title: step.title,
            status: "success",
            durationMs: stepDuration,
            message: getSimulatedMessage(step),
          },
        ]);

        if (idx === steps.length - 1) {
          setIsRunning(false);
          setIsFinished(true);
          if (onSimulationComplete) onSimulationComplete();
        }
      }, accumulatedTime);
    });
  };

  const getSimulatedMessage = (step: WorkflowStep) => {
    switch (step.type) {
      case "registration":
        return `Customer intake verified. Seat #${Math.floor(Math.random() * 20 + 30)} allocated. Concurrency lock acquired.`;
      case "payment":
        return `PayPal Sandbox capture approved for $${step.config.price || 20}.00 ${step.config.currency || "USD"}. Order ID: PAYID-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
      case "verification":
        return `Cryptographic IPN signature verified against PayPal root certificate. Double-charge fraud check passed.`;
      case "email":
        return `Confirmation ticket delivered via transactional SMTP mesh to simulated student inbox.`;
      case "analytics":
        return `Dashboard telemetry synced: Seat balance decremented, revenue credited, operator alerted.`;
      default:
        return `Step executed successfully.`;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl z-10 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h3 className="font-semibold text-white text-base">
              Workflow Execution Simulator (Frontend Only)
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Target Workflow Info */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
            <div className="text-xs font-mono uppercase text-slate-400 mb-1">
              Executing Pipeline
            </div>
            <div className="text-sm font-bold text-white">{workflow.title}</div>
            <div className="text-xs text-slate-400 mt-1">
              Simulated Customer: <strong className="text-slate-200">Alex Morgan (alex.morgan@test.io)</strong>
            </div>
          </div>

          {/* Steps Progress */}
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center justify-between">
              <span>Step-by-Step Execution Mesh</span>
              {isRunning && (
                <span className="text-indigo-400 inline-flex items-center gap-1">
                  <Clock className="w-3 h-3 animate-spin" /> Live Processing...
                </span>
              )}
            </div>

            <div className="space-y-2.5">
              {workflow.steps.map((step, idx) => {
                const log = stepLogs.find((l) => l.stepId === step.id);
                const isCurrent = currentStepIndex === idx && isRunning;
                const isDone = !!log;

                return (
                  <div
                    key={step.id}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isDone
                        ? "bg-slate-950/80 border-emerald-500/40"
                        : isCurrent
                        ? "bg-slate-900 border-indigo-500 ring-1 ring-indigo-500/50 shadow-md"
                        : "bg-slate-950/40 border-slate-800/80 opacity-60"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {isDone ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : isCurrent ? (
                          <Clock className="w-4 h-4 text-indigo-400 animate-spin" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-700 flex items-center justify-center text-[10px] text-slate-500">
                            {idx + 1}
                          </div>
                        )}
                        <span className="text-xs font-semibold text-white">
                          {step.title}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        {isDone ? `${log.durationMs}ms` : step.type}
                      </span>
                    </div>

                    {log && (
                      <div className="mt-1.5 pl-6 text-xs text-slate-300 font-mono leading-relaxed">
                        {log.message}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Simulation Completed Banner */}
          {isFinished && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                <div>
                  <div className="text-xs font-bold text-white">
                    Workflow Executed Successfully with 100% Quality
                  </div>
                  <div className="text-[11px] text-emerald-300/80">
                    PayPal payment captured, transaction verified, and confirmation receipt delivered.
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={resetAndRun}
                leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
              >
                Re-Run
              </Button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <Link href={`/preview/${workflow.id}`} target="_blank">
            <Button
              variant="secondary"
              size="sm"
              rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
            >
              Open Live Customer Form
            </Button>
          </Link>
          <Button variant="primary" size="sm" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};
