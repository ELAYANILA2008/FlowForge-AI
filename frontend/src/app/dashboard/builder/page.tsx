"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  ArrowRight,
  Play,
  Save,
  CheckCircle2,
  Sliders,
  ExternalLink,
  Layers,
  ChevronRight,
  RefreshCw,
  Info,
  Check,
  Edit2,
} from "lucide-react";
import { TopNav } from "@/components/dashboard/TopNav";
import { NodeCard } from "@/components/builder/NodeCard";
import { StepConfigDrawer } from "@/components/builder/StepConfigDrawer";
import { RunSimulationModal } from "@/components/builder/RunSimulationModal";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Workflow, WorkflowStep } from "@/types/workflow";
import { WorkflowService } from "@/services/api";
import { createWorkflowFromPrompt } from "@/services/workflowGenerator";
import Link from "next/link";

const PRESET_PROMPTS = [
  {
    title: "Photography Workshop",
    prompt:
      "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails.",
  },
  {
    title: "AI Founders Masterclass",
    prompt:
      "Host a free masterclass for 200 founders with automated Zoom links, company verification, and Discord invites.",
  },
  {
    title: "Full-Stack Bootcamp",
    prompt:
      "Create a 25-seat developer bootcamp registration for $150 with PayPal invoice generation and student onboarding survey.",
  },
  {
    title: "Executive Consulting Session",
    prompt:
      "Book 10 private 1-on-1 strategy sessions at $350 each with PayPal deposit and Google Meet calendar dispatch.",
  },
];

function WorkflowBuilderContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("id");

  const [promptText, setPromptText] = useState(
    "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationPhase, setGenerationPhase] = useState<string>("");
  const [workflow, setWorkflow] = useState<Workflow>(() =>
    createWorkflowFromPrompt(
      "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
    )
  );
  const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
  const [editingStep, setEditingStep] = useState<WorkflowStep | null>(null);
  const [isSimulationOpen, setIsSimulationOpen] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [customTitle, setCustomTitle] = useState("");

  // Load existing workflow if ID was provided in URL
  useEffect(() => {
    async function loadInitial() {
      if (initialId) {
        try {
          const loaded = await WorkflowService.getWorkflowById(initialId);
          if (loaded) {
            setWorkflow(loaded);
            setPromptText(loaded.prompt || loaded.title);
            setSelectedStep(loaded.steps[0] || null);
            setCustomTitle(loaded.title);
          }
        } catch (e) {
          console.error("Failed to load workflow from param", e);
        }
      } else {
        setSelectedStep(workflow.steps[0] || null);
        setCustomTitle(workflow.title);
      }
    }
    loadInitial();
  }, [initialId]);

  const handleGenerate = async () => {
    if (!promptText.trim()) return;
    setIsGenerating(true);
    setIsSaved(false);

    const phases = [
      "Analyzing natural-language instructions...",
      "Extracting capacity constraints and fee structures...",
      "Generating responsive customer intake portal...",
      "Binding PayPal payment gateway and IPN listener...",
      "Wiring ticket delivery and telemetry mesh...",
    ];

    for (let i = 0; i < phases.length; i++) {
      setGenerationPhase(phases[i]);
      await new Promise((r) => setTimeout(r, 240));
    }

    try {
      const generated = await WorkflowService.generateWorkflow(promptText);
      setWorkflow(generated);
      setSelectedStep(generated.steps[0]);
      setCustomTitle(generated.title);
    } catch (err) {
      console.error(err);
    } finally {
      setIsGenerating(false);
      setGenerationPhase("");
    }
  };

  const handleSave = async () => {
    try {
      const toSave = {
        ...workflow,
        title: customTitle || workflow.title,
      };
      await WorkflowService.saveWorkflow(toSave);
      setWorkflow(toSave);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      console.error("Failed to save workflow", err);
    }
  };

  const handleUpdateStep = (updated: WorkflowStep) => {
    setWorkflow((prev) => ({
      ...prev,
      steps: prev.steps.map((s) => (s.id === updated.id ? updated : s)),
    }));
    if (selectedStep?.id === updated.id) {
      setSelectedStep(updated);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <TopNav
        title="AI Workflow Builder"
        subtitle="Natural-Language to Autonomous Business Pipeline"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant={isSaved ? "emerald" : "outline"}
              size="sm"
              onClick={handleSave}
              leftIcon={isSaved ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
            >
              {isSaved ? "Saved Successfully!" : "Save Workflow"}
            </Button>
            <Button
              variant="emerald"
              size="sm"
              onClick={() => setIsSimulationOpen(true)}
              leftIcon={<Play className="w-3.5 h-3.5 fill-current" />}
            >
              Run Simulation
            </Button>
          </div>
        }
      />

      <main className="p-4 sm:p-6 md:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full flex-1">
        {/* Natural Language Prompt Input Bar */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <label className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">
                Describe Your Business Operation
              </label>
            </div>
            <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
              Natural-Language AI Compiler
            </span>
          </div>

          <div className="relative">
            <textarea
              rows={3}
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              placeholder="e.g. Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-3.5 sm:p-4 text-sm sm:text-base text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-sans leading-relaxed resize-none"
            />
          </div>

          {/* Preset chips */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-[11px] text-slate-400 mr-1">Presets:</span>
            {PRESET_PROMPTS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setPromptText(preset.prompt);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 hover:text-white hover:border-indigo-500/50 transition-colors"
              >
                {preset.title}
              </button>
            ))}
          </div>

          {/* Generate Button Row */}
          <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="text-xs text-slate-400 flex items-center gap-1.5 font-mono">
              {isGenerating ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
                  <span className="text-indigo-300">{generationPhase}</span>
                </>
              ) : (
                <span>
                  Targeting: <strong>5 Connected Operational Steps</strong>
                </span>
              )}
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={handleGenerate}
              isLoading={isGenerating}
              rightIcon={<ArrowRight className="w-4 h-4 ml-1" />}
              className="w-full sm:w-auto"
            >
              Generate Workflow
            </Button>
          </div>
        </div>

        {/* Workflow Title & Meta Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="active" dot>
                {workflow.status.toUpperCase()}
              </Badge>
              {isEditingTitle ? (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    className="bg-slate-950 border border-indigo-500 rounded px-2 py-0.5 text-sm text-white font-bold"
                  />
                  <button
                    onClick={() => {
                      setIsEditingTitle(false);
                      setWorkflow((prev) => ({ ...prev, title: customTitle }));
                    }}
                    className="text-xs text-emerald-400 font-medium px-2 py-1 bg-slate-800 rounded hover:bg-slate-700"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 group">
                  <h2 className="text-base sm:text-lg font-bold text-white">
                    {workflow.title}
                  </h2>
                  <button
                    onClick={() => {
                      setCustomTitle(workflow.title);
                      setIsEditingTitle(true);
                    }}
                    className="text-slate-500 hover:text-slate-300 opacity-60 group-hover:opacity-100"
                    title="Rename workflow"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">{workflow.description}</p>
          </div>

          <div className="flex items-center gap-2 self-stretch sm:self-auto justify-end">
            <Link href={`/preview/${workflow.id}`} target="_blank">
              <Button
                variant="outline"
                size="sm"
                rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
              >
                Preview Customer Portal
              </Button>
            </Link>
          </div>
        </div>

        {/* Visual Connected Pipeline Canvas */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Synthesized Execution Pipeline</span>
            </div>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Click any node to inspect parameters or tweak logic
            </span>
          </div>

          {/* Node Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {workflow.steps.map((step, idx) => (
              <NodeCard
                key={step.id}
                step={step}
                index={idx}
                totalSteps={workflow.steps.length}
                isSelected={selectedStep?.id === step.id}
                onSelect={(s) => setSelectedStep(s)}
                onConfigure={(s) => setEditingStep(s)}
              />
            ))}
          </div>
        </div>

        {/* Active Node Detail Inspector */}
        {selectedStep && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-mono uppercase text-indigo-400 tracking-wider">
                  Step {selectedStep.order} · {selectedStep.type}
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {selectedStep.title}
                </h3>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setEditingStep(selectedStep)}
                leftIcon={<Sliders className="w-3.5 h-3.5" />}
              >
                Configure Settings
              </Button>
            </div>

            <p className="mt-4 text-sm text-slate-300 leading-relaxed">
              {selectedStep.description}
            </p>

            <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                <span className="block text-[10px] font-mono uppercase text-slate-500 mb-1">
                  Parameters
                </span>
                <div className="text-slate-200 font-mono">
                  {selectedStep.config.capacity && `Capacity: ${selectedStep.config.capacity} attendees`}
                  {selectedStep.config.price !== undefined && `Fee: $${selectedStep.config.price} USD`}
                  {selectedStep.config.emailTemplate && `Template: ${selectedStep.config.emailTemplate}`}
                  {!selectedStep.config.capacity && !selectedStep.config.price && "Automated Telemetry Sync"}
                </div>
              </div>

              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                <span className="block text-[10px] font-mono uppercase text-slate-500 mb-1">
                  Target Verification
                </span>
                <div className="text-emerald-400 font-mono">
                  100% Cryptographic Signature Guard
                </div>
              </div>

              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                <span className="block text-[10px] font-mono uppercase text-slate-500 mb-1">
                  Latency Benchmark
                </span>
                <div className="text-indigo-300 font-mono">
                  {selectedStep.metrics?.avgExecutionTimeMs || 180}ms average response
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Step Config Drawer */}
      <StepConfigDrawer
        step={editingStep}
        isOpen={!!editingStep}
        onClose={() => setEditingStep(null)}
        onSave={handleUpdateStep}
      />

      {/* Step-by-Step Simulation Modal */}
      <RunSimulationModal
        workflow={workflow}
        isOpen={isSimulationOpen}
        onClose={() => setIsSimulationOpen(false)}
        onSimulationComplete={() => {
          setWorkflow((prev) => ({
            ...prev,
            stats: {
              ...prev.stats,
              totalRuns: prev.stats.totalRuns + 1,
              successfulRuns: prev.stats.successfulRuns + 1,
            },
          }));
        }}
      />
    </div>
  );
}

export default function AIWorkflowBuilderPage() {
  return (
    <Suspense
      fallback={
        <div className="p-12 text-center text-slate-400 font-mono animate-pulse">
          Loading AI Workflow Builder...
        </div>
      }
    >
      <WorkflowBuilderContent />
    </Suspense>
  );
}
