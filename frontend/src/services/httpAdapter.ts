import {
  IWorkflowService,
  IMetricsService,
  IRegistrationService,
} from "@/types/api";
import { Workflow, ExecutionLog } from "@/types/workflow";
import { DashboardMetrics, AgentPerformanceMetric, ActivityFeedItem } from "@/types/metrics";
import { RegistrationFormData, RegistrationSubmission } from "@/types/registration";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `API Request Failed [${response.status} ${response.statusText}] at ${endpoint}: ${errorBody}`
    );
  }

  return response.json();
}

export const HttpWorkflowService: IWorkflowService = {
  async getAllWorkflows(): Promise<Workflow[]> {
    return apiFetch<Workflow[]>("/workflows");
  },

  async getWorkflowById(id: string): Promise<Workflow | null> {
    return apiFetch<Workflow>(`/workflows/${id}`);
  },

  async generateWorkflow(prompt: string): Promise<Workflow> {
    return apiFetch<Workflow>("/workflows/generate", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
  },

  async saveWorkflow(workflow: Workflow): Promise<Workflow> {
    return apiFetch<Workflow>(`/workflows/${workflow.id}`, {
      method: "PUT",
      body: JSON.stringify(workflow),
    });
  },

  async deleteWorkflow(id: string): Promise<boolean> {
    await apiFetch<{ success: boolean }>(`/workflows/${id}`, {
      method: "DELETE",
    });
    return true;
  },

  async runWorkflow(workflowId: string, payload?: Record<string, any>): Promise<ExecutionLog> {
    return apiFetch<ExecutionLog>(`/workflows/${workflowId}/run`, {
      method: "POST",
      body: JSON.stringify(payload || {}),
    });
  },

  async getExecutionHistory(workflowId: string): Promise<ExecutionLog[]> {
    return apiFetch<ExecutionLog[]>(`/workflows/${workflowId}/executions`);
  },
};

export const HttpMetricsService: IMetricsService = {
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return apiFetch<DashboardMetrics>("/metrics/dashboard");
  },

  async getAgentPerformance(): Promise<AgentPerformanceMetric[]> {
    return apiFetch<AgentPerformanceMetric[]>("/metrics/agents");
  },

  async getActivityFeed(): Promise<ActivityFeedItem[]> {
    return apiFetch<ActivityFeedItem[]>("/activity");
  },
};

export const HttpRegistrationService: IRegistrationService = {
  async submitRegistration(
    workflowId: string,
    data: RegistrationFormData
  ): Promise<RegistrationSubmission> {
    return apiFetch<RegistrationSubmission>(`/registration/${workflowId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getRegistrationStatus(submissionId: string): Promise<RegistrationSubmission | null> {
    return apiFetch<RegistrationSubmission>(`/registration/status/${submissionId}`);
  },
};
