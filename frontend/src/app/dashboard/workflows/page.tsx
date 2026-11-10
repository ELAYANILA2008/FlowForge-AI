"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Layers,
  Search,
  Plus,
  Play,
  ArrowRight,
  ExternalLink,
  Edit,
  Pause,
  Trash2,
} from "lucide-react";
import { TopNav } from "@/components/dashboard/TopNav";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { WorkflowService } from "@/services/api";
import { Workflow } from "@/types/workflow";
import { RunSimulationModal } from "@/components/builder/RunSimulationModal";

export default function WorkflowsManagementPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedWorkflowForRun, setSelectedWorkflowForRun] = useState<Workflow | null>(null);

  const loadData = async () => {
    try {
      const data = await WorkflowService.getAllWorkflows();
      setWorkflows(data);
    } catch (err) {
      console.error("Failed to load workflows", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleStatus = async (wf: Workflow) => {
    const newStatus = wf.status === "active" ? "paused" : "active";
    const updated = { ...wf, status: newStatus as any };
    await WorkflowService.saveWorkflow(updated);
    setWorkflows((prev) => prev.map((w) => (w.id === wf.id ? updated : w)));
  };

  const handleDeleteWorkflow = async (id: string, title: string) => {
    if (confirm(`Are you sure you want to delete "${title}"?`)) {
      await WorkflowService.deleteWorkflow(id);
      setWorkflows((prev) => prev.filter((w) => w.id !== id));
    }
  };

  const filteredWorkflows = workflows.filter((wf) => {
    const matchesSearch =
      wf.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wf.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wf.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus =
      statusFilter === "all" || wf.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <TopNav
        title="Workflow Management"
        subtitle="Manage, monitor, and run all business operations"
        actions={
          <Link href="/dashboard/builder">
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-3.5 h-3.5" />}
            >
              New Workflow
            </Button>
          </Link>
        }
      />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl mx-auto w-full flex-1">
        {/* Controls: Search and Filter Tabs */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search workflows by title, tag, or prompt..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Status Tabs */}
          <div className="flex items-center gap-1 p-1 bg-slate-950 border border-slate-800 rounded-lg text-xs self-start sm:self-auto overflow-x-auto">
            {["all", "active", "paused", "completed", "failed"].map((tab) => (
              <button
                key={tab}
                onClick={() => setStatusFilter(tab)}
                className={`px-3 py-1.5 rounded-md font-medium capitalize transition-colors ${
                  statusFilter === tab
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Workflows List */}
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm font-mono animate-pulse">
            Loading workflows...
          </div>
        ) : filteredWorkflows.length === 0 ? (
          <div className="p-12 text-center bg-slate-900/40 border border-slate-800 rounded-2xl">
            <p className="text-slate-400 text-sm">No workflows found matching your filter.</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => {
                setSearchQuery("");
                setStatusFilter("all");
              }}
            >
              Reset Filters
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredWorkflows.map((wf) => (
              <div
                key={wf.id}
                className="bg-slate-900/70 border border-slate-800/90 hover:border-slate-700 rounded-2xl p-5 sm:p-6 transition-all duration-200 shadow-lg hover:shadow-xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6"
              >
                {/* Workflow Left Info */}
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <Badge
                      variant={
                        wf.status === "active"
                          ? "active"
                          : wf.status === "completed"
                          ? "completed"
                          : wf.status === "failed"
                          ? "failed"
                          : "paused"
                      }
                      dot
                    >
                      {wf.status.toUpperCase()}
                    </Badge>
                    <Link
                      href={`/dashboard/workflows/${wf.id}`}
                      className="text-base font-bold text-white hover:text-indigo-400 transition-colors"
                    >
                      {wf.title}
                    </Link>
                  </div>

                  <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
                    {wf.description}
                  </p>

                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    {wf.tags.map((tag, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400"
                      >
                        #{tag}
                      </span>
                    ))}
                    <span className="text-[10px] text-slate-500 font-mono">
                      · {wf.steps.length} Steps Pipeline
                    </span>
                  </div>
                </div>

                {/* Workflow Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs font-mono text-right w-full lg:w-auto lg:min-w-[320px]">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Runs</div>
                    <div className="font-bold text-slate-200">{wf.stats.totalRuns}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Revenue</div>
                    <div className="font-bold text-emerald-400">
                      ${wf.stats.totalRevenue.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Capacity</div>
                    <div className="font-bold text-indigo-300">
                      {wf.stats.totalRegistrations}/{wf.stats.capacityLimit}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase">Quality</div>
                    <div className="font-bold text-teal-400">
                      {wf.stats.reliabilityScore}%
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 w-full lg:w-auto justify-end border-t lg:border-t-0 pt-3 lg:pt-0 border-slate-800">
                  <button
                    onClick={() => setSelectedWorkflowForRun(wf)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition-colors"
                    title="Simulate workflow execution"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run</span>
                  </button>
                  <button
                    onClick={() => handleToggleStatus(wf)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                    title={wf.status === "active" ? "Pause Workflow" : "Resume Workflow"}
                  >
                    <Pause className="w-3.5 h-3.5" />
                  </button>
                  <Link href={`/preview/${wf.id}`} target="_blank">
                    <Button variant="ghost" size="sm" title="Preview public form">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Button>
                  </Link>
                  <Link href={`/dashboard/builder?id=${wf.id}`}>
                    <Button variant="secondary" size="sm" title="Edit in builder">
                      <Edit className="w-3.5 h-3.5" />
                    </Button>
                  </Link>
                  <Link href={`/dashboard/workflows/${wf.id}`}>
                    <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3 h-3" />}>
                      Details
                    </Button>
                  </Link>
                  <button
                    onClick={() => handleDeleteWorkflow(wf.id, wf.title)}
                    className="p-1.5 rounded-lg text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors ml-1"
                    title="Delete workflow"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Runner Simulation Modal */}
      {selectedWorkflowForRun && (
        <RunSimulationModal
          workflow={selectedWorkflowForRun}
          isOpen={!!selectedWorkflowForRun}
          onClose={() => {
            setSelectedWorkflowForRun(null);
            loadData();
          }}
        />
      )}
    </div>
  );
}
