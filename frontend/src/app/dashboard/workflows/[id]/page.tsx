"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Play,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Clock,
  Edit,
  Pause,
  UserCheck,
  CreditCard,
  ShieldCheck,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { TopNav } from "@/components/dashboard/TopNav";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { WorkflowService } from "@/services/api";
import { Workflow, ExecutionLog } from "@/types/workflow";
import { RunSimulationModal } from "@/components/builder/RunSimulationModal";

export default function WorkflowDetailPage() {
  const params = useParams();
  const workflowId = (params?.id as string) || "wf-photo-001";

  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [executions, setExecutions] = useState<ExecutionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedLogId, setExpandedLogId] = useState<string | null>("exec-9821");
  const [isSimModalOpen, setIsSimModalOpen] = useState(false);

  const loadData = async () => {
    try {
      const wf = await WorkflowService.getWorkflowById(workflowId);
      const execs = await WorkflowService.getExecutionHistory(workflowId);
      setWorkflow(wf);
      setExecutions(execs);
    } catch (err) {
      console.error("Failed to load workflow detail", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [workflowId]);

  const handleToggleStatus = async () => {
    if (!workflow) return;
    const newStatus = workflow.status === "active" ? "paused" : "active";
    const updated = { ...workflow, status: newStatus as any };
    await WorkflowService.saveWorkflow(updated);
    setWorkflow(updated);
  };

  if (loading || !workflow) {
    return (
      <div className="flex-1 flex flex-col">
        <TopNav title="Workflow Details" />
        <div className="p-8 text-center text-slate-400 font-mono animate-pulse">
          Loading workflow specifications...
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <TopNav
        title={workflow.title}
        subtitle={`Workflow ID: ${workflow.id}`}
        actions={
          <div className="flex items-center gap-2">
            <Link href={`/dashboard/builder?id=${workflow.id}`}>
              <Button
                variant="secondary"
                size="sm"
                leftIcon={<Edit className="w-3.5 h-3.5" />}
              >
                Edit
              </Button>
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={handleToggleStatus}
              leftIcon={<Pause className="w-3.5 h-3.5" />}
            >
              {workflow.status === "active" ? "Pause" : "Resume"}
            </Button>
            <Link href={`/preview/${workflow.id}`} target="_blank">
              <Button
                variant="outline"
                size="sm"
                rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
              >
                Customer Page
              </Button>
            </Link>
            <Button
              variant="emerald"
              size="sm"
              onClick={() => setIsSimModalOpen(true)}
              leftIcon={<Play className="w-3.5 h-3.5 fill-current" />}
            >
              Run Execution
            </Button>
          </div>
        }
      />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full flex-1">
        {/* Back Link */}
        <Link
          href="/dashboard/workflows"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to all workflows
        </Link>

        {/* Workflow Summary Header Card */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <Badge variant={workflow.status === "active" ? "active" : "paused"} dot>
                  {workflow.status.toUpperCase()}
                </Badge>
                <h2 className="text-lg sm:text-xl font-bold text-white">{workflow.title}</h2>
              </div>
              <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
                {workflow.description}
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono self-end sm:self-auto">
              <div className="text-right">
                <span className="text-[10px] uppercase text-slate-500 block">Created</span>
                <span className="text-slate-300">
                  {new Date(workflow.createdAt).toLocaleDateString()}
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase text-slate-500 block">Last Run</span>
                <span className="text-slate-300">
                  {new Date(workflow.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>

          {/* 4 Statistics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 mb-1">
                <UserCheck className="w-3.5 h-3.5 text-indigo-400" /> Registrations
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-white">
                {workflow.stats.totalRegistrations}{" "}
                <span className="text-xs text-slate-500 font-normal">
                  / {workflow.stats.capacityLimit} max
                </span>
              </div>
              <div className="mt-2 w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full"
                  style={{
                    width: `${Math.min(
                      100,
                      (workflow.stats.totalRegistrations / workflow.stats.capacityLimit) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 mb-1">
                <CreditCard className="w-3.5 h-3.5 text-emerald-400" /> Revenue Captured
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-emerald-400">
                ${workflow.stats.totalRevenue.toLocaleString()}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">PayPal Verified</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 mb-1">
                <ShieldCheck className="w-3.5 h-3.5 text-teal-400" /> Quality & Reliability
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-teal-400">
                {workflow.stats.reliabilityScore}%
              </div>
              <div className="text-[11px] text-slate-500 mt-1">0 unhandled exceptions</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 mb-1">
                <Clock className="w-3.5 h-3.5 text-sky-400" /> Avg Latency
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-white">
                {workflow.stats.avgRunDurationMs}ms
              </div>
              <div className="text-[11px] text-slate-500 mt-1">5 parallel steps</div>
            </div>
          </div>
        </div>

        {/* Configured Steps Breakdown */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" /> Pipeline Configuration ({workflow.steps.length} Steps)
            </h3>
            <span className="text-xs text-slate-400 font-mono hidden sm:inline">
              Deterministic Step Sequence
            </span>
          </div>

          <div className="space-y-3">
            {workflow.steps.map((step, idx) => (
              <div
                key={step.id}
                className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-800 text-xs font-mono font-bold flex items-center justify-center text-slate-300">
                    {idx + 1}
                  </span>
                  <div>
                    <div className="text-xs font-bold text-white flex items-center gap-2">
                      <span>{step.title}</span>
                      <span className="text-[10px] font-mono text-slate-400 uppercase">
                        [{step.type}]
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">{step.description}</div>
                  </div>
                </div>

                <div className="text-right text-xs font-mono text-slate-400">
                  {step.metrics && (
                    <span className="text-emerald-400">{step.metrics.successRate}% rate</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Execution History Table & Logs */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-sm font-semibold text-white">Execution Audit Trail</h3>
              <p className="text-xs text-slate-400">
                Detailed step results, input payloads, and timestamps for every run
              </p>
            </div>
            <Badge variant="optimal">Cryptographically Logged</Badge>
          </div>

          <div className="space-y-3">
            {executions.map((exec) => {
              const isExpanded = expandedLogId === exec.id;

              return (
                <div
                  key={exec.id}
                  className="rounded-xl bg-slate-950 border border-slate-800 overflow-hidden"
                >
                  {/* Execution Header row */}
                  <div
                    onClick={() => setExpandedLogId(isExpanded ? null : exec.id)}
                    className="p-4 cursor-pointer hover:bg-slate-900/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {exec.status === "success" ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                      )}
                      <div>
                        <div className="text-xs font-bold text-white flex items-center gap-2">
                          <span className="font-mono text-indigo-300">{exec.id}</span>
                          <span>·</span>
                          <span>{exec.customer?.name || "Customer Registration"}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {exec.customer?.email} · {exec.trigger}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                      <span>{exec.durationMs}ms duration</span>
                      <span>{new Date(exec.timestamp).toLocaleTimeString()}</span>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Step Log Details */}
                  {isExpanded && (
                    <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 space-y-2">
                      <div className="text-[11px] font-mono uppercase text-slate-400 mb-2">
                        Individual Step Payloads & Verification
                      </div>
                      {exec.stepResults.map((sRes, sIdx) => (
                        <div
                          key={sIdx}
                          className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                        >
                          <div className="flex items-center gap-2">
                            {sRes.status === "success" ? (
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                            ) : sRes.status === "failed" ? (
                              <XCircle className="w-3.5 h-3.5 text-rose-400" />
                            ) : (
                              <Clock className="w-3.5 h-3.5 text-slate-500" />
                            )}
                            <span className="font-semibold text-slate-200">
                              {sRes.stepTitle}:
                            </span>
                            <span className="text-slate-400 font-mono text-[11px]">
                              {sRes.message}
                            </span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-400 self-end sm:self-auto">
                            {sRes.durationMs}ms
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* Runner Modal */}
      <RunSimulationModal
        workflow={workflow}
        isOpen={isSimModalOpen}
        onClose={() => {
          setIsSimModalOpen(false);
          loadData();
        }}
      />
    </div>
  );
}
