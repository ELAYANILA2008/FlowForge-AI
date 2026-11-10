import {
  IWorkflowService,
  IMetricsService,
  IRegistrationService,
} from "@/types/api";
import { Workflow, ExecutionLog } from "@/types/workflow";
import { DashboardMetrics, AgentPerformanceMetric, ActivityFeedItem } from "@/types/metrics";
import { RegistrationFormData, RegistrationSubmission } from "@/types/registration";
import {
  SAMPLE_WORKFLOWS,
  SAMPLE_EXECUTION_LOGS,
  SAMPLE_DASHBOARD_METRICS,
  SAMPLE_AGENT_PERFORMANCE,
  SAMPLE_ACTIVITY_FEED,
} from "./mockData";
import { createWorkflowFromPrompt } from "./workflowGenerator";

const STORAGE_KEYS = {
  WORKFLOWS: "flowforge_demo_workflows",
  EXECUTIONS: "flowforge_demo_executions",
  ACTIVITY: "flowforge_demo_activity",
};

function getStored<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    console.warn(`Failed to read ${key} from localStorage, using demo fallback`, e);
    return fallback;
  }
}

function setStored<T>(key: string, val: T): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch (e) {
    console.warn(`Failed to persist ${key} to localStorage`, e);
  }
}

let memoryWorkflows: Workflow[] = [...SAMPLE_WORKFLOWS];
let memoryExecutions: ExecutionLog[] = [...SAMPLE_EXECUTION_LOGS];
let memoryActivity: ActivityFeedItem[] = [...SAMPLE_ACTIVITY_FEED];

function getWorkflows(): Workflow[] {
  const stored = getStored<Workflow[]>(STORAGE_KEYS.WORKFLOWS, memoryWorkflows);
  memoryWorkflows = stored;
  return memoryWorkflows;
}

function saveWorkflows(list: Workflow[]): void {
  memoryWorkflows = list;
  setStored(STORAGE_KEYS.WORKFLOWS, list);
}

function getExecutions(): ExecutionLog[] {
  const stored = getStored<ExecutionLog[]>(STORAGE_KEYS.EXECUTIONS, memoryExecutions);
  memoryExecutions = stored;
  return memoryExecutions;
}

function saveExecutions(list: ExecutionLog[]): void {
  memoryExecutions = list;
  setStored(STORAGE_KEYS.EXECUTIONS, list);
}

function getActivity(): ActivityFeedItem[] {
  const stored = getStored<ActivityFeedItem[]>(STORAGE_KEYS.ACTIVITY, memoryActivity);
  memoryActivity = stored;
  return memoryActivity;
}

function saveActivity(list: ActivityFeedItem[]): void {
  memoryActivity = list;
  setStored(STORAGE_KEYS.ACTIVITY, list);
}

export const MockWorkflowService: IWorkflowService = {
  async getAllWorkflows(): Promise<Workflow[]> {
    await new Promise((r) => setTimeout(r, 120));
    return [...getWorkflows()];
  },

  async getWorkflowById(id: string): Promise<Workflow | null> {
    await new Promise((r) => setTimeout(r, 80));
    const all = getWorkflows();
    return all.find((w) => w.id === id) || all[0] || null;
  },

  async generateWorkflow(prompt: string): Promise<Workflow> {
    await new Promise((r) => setTimeout(r, 500)); // Simulate AI engine latency
    const newWf = createWorkflowFromPrompt(prompt);
    const all = getWorkflows();
    const updated = [newWf, ...all];
    saveWorkflows(updated);
    return newWf;
  },

  async saveWorkflow(workflow: Workflow): Promise<Workflow> {
    await new Promise((r) => setTimeout(r, 150));
    const all = getWorkflows();
    const idx = all.findIndex((w) => w.id === workflow.id);
    let updated: Workflow[];
    if (idx >= 0) {
      updated = [...all];
      updated[idx] = { ...workflow, updatedAt: new Date().toISOString() };
    } else {
      updated = [workflow, ...all];
    }
    saveWorkflows(updated);
    return workflow;
  },

  async deleteWorkflow(id: string): Promise<boolean> {
    await new Promise((r) => setTimeout(r, 100));
    const all = getWorkflows();
    const filtered = all.filter((w) => w.id !== id);
    saveWorkflows(filtered);
    return true;
  },

  async runWorkflow(workflowId: string, payload?: Record<string, any>): Promise<ExecutionLog> {
    await new Promise((r) => setTimeout(r, 600));
    const all = getWorkflows();
    const target = all.find((w) => w.id === workflowId) || all[0];
    const now = new Date().toISOString();

    const newLog: ExecutionLog = {
      id: `exec-${Date.now().toString(36)}`,
      workflowId: target.id,
      timestamp: now,
      status: "success",
      trigger: "manual_test",
      durationMs: 1140,
      customer: {
        name: payload?.studentName || "Simulated Student",
        email: payload?.studentEmail || "student@example.com",
      },
      stepResults: target.steps.map((s, idx) => ({
        stepId: s.id,
        stepTitle: s.title,
        status: "success",
        durationMs: 140 + idx * 60,
        message: `Verified step: ${s.title}`,
      })),
    };

    target.stats.totalRuns += 1;
    target.stats.successfulRuns += 1;
    const paymentStep = target.steps.find((s) => s.type === "payment");
    if (paymentStep?.config.price) {
      target.stats.totalRevenue += paymentStep.config.price;
      target.stats.totalRegistrations += 1;
    }
    saveWorkflows(all);

    const execs = [newLog, ...getExecutions()];
    saveExecutions(execs);

    const acts = [
      {
        id: `act-${Date.now()}`,
        workflowId: target.id,
        workflowTitle: target.title,
        type: "payment" as const,
        title: "Test Run Succeeded",
        description: `Executed 5 steps in 1.14s for ${target.title}`,
        timestamp: "Just now",
        status: "success" as const,
      },
      ...getActivity(),
    ];
    saveActivity(acts);

    return newLog;
  },

  async getExecutionHistory(workflowId: string): Promise<ExecutionLog[]> {
    await new Promise((r) => setTimeout(r, 100));
    return getExecutions().filter((l) => l.workflowId === workflowId);
  },
};

export const MockMetricsService: IMetricsService = {
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    await new Promise((r) => setTimeout(r, 100));
    const workflows = getWorkflows();
    const totalWfs = workflows.length;
    const activeWfs = workflows.filter((w) => w.status === "active").length;
    const totalRegs = workflows.reduce((acc, w) => acc + (w.stats?.totalRegistrations || 0), 0);
    const totalRev = workflows.reduce((acc, w) => acc + (w.stats?.totalRevenue || 0), 0);

    return {
      ...SAMPLE_DASHBOARD_METRICS,
      totalWorkflows: totalWfs,
      activeWorkflows: activeWfs,
      totalRegistrations: Math.max(totalRegs, SAMPLE_DASHBOARD_METRICS.totalRegistrations),
      totalRevenueUsd: Math.max(totalRev, SAMPLE_DASHBOARD_METRICS.totalRevenueUsd),
    };
  },

  async getAgentPerformance(): Promise<AgentPerformanceMetric[]> {
    await new Promise((r) => setTimeout(r, 100));
    return [...SAMPLE_AGENT_PERFORMANCE];
  },

  async getActivityFeed(): Promise<ActivityFeedItem[]> {
    await new Promise((r) => setTimeout(r, 80));
    return [...getActivity()];
  },
};

export const MockRegistrationService: IRegistrationService = {
  async submitRegistration(
    workflowId: string,
    data: RegistrationFormData
  ): Promise<RegistrationSubmission> {
    await new Promise((r) => setTimeout(r, 400));
    const all = getWorkflows();
    const target = all.find((w) => w.id === workflowId) || all[0];
    const fee = target.steps.find((s) => s.type === "payment")?.config.price || 20;
    const currency = target.steps.find((s) => s.type === "payment")?.config.currency || "USD";

    target.stats.totalRegistrations += 1;
    target.stats.totalRevenue += fee;
    target.stats.totalRuns += 1;
    target.stats.successfulRuns += 1;
    saveWorkflows(all);

    const submission: RegistrationSubmission = {
      id: `reg-${Date.now().toString(36)}`,
      workflowId: target.id,
      studentName: data.studentName,
      studentEmail: data.studentEmail,
      feeAmount: fee,
      currency,
      paymentStatus: "paid",
      paypalTransactionId: `PAYID-${Math.random().toString(36).substring(2, 9).toUpperCase()}`,
      emailConfirmed: true,
      registeredAt: new Date().toISOString(),
    };

    const acts = [
      {
        id: `act-${Date.now()}`,
        workflowId: target.id,
        workflowTitle: target.title,
        type: "registration" as const,
        title: "New Student Registered",
        description: `${data.studentName} registered for ${target.title}`,
        timestamp: "Just now",
        amount: fee,
        status: "success" as const,
      },
      ...getActivity(),
    ];
    saveActivity(acts);

    return submission;
  },

  async getRegistrationStatus(submissionId: string): Promise<RegistrationSubmission | null> {
    await new Promise((r) => setTimeout(r, 80));
    return null;
  },
};
