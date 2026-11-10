import { Workflow, ExecutionLog } from "./workflow";
import { DashboardMetrics, AgentPerformanceMetric, ActivityFeedItem } from "./metrics";
import { RegistrationFormData, RegistrationSubmission } from "./registration";

/**
 * Standard API Response envelope for FastAPI backend integration
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
  isDemonstrationData?: boolean;
}

/**
 * Request payload for AI Engine workflow generation
 */
export interface GenerateWorkflowRequest {
  prompt: string;
  options?: {
    defaultCurrency?: string;
    strictMode?: boolean;
    timeoutSeconds?: number;
  };
}

/**
 * Service contract for Workflow operations
 */
export interface IWorkflowService {
  getAllWorkflows(): Promise<Workflow[]>;
  getWorkflowById(id: string): Promise<Workflow | null>;
  generateWorkflow(prompt: string): Promise<Workflow>;
  saveWorkflow(workflow: Workflow): Promise<Workflow>;
  deleteWorkflow(id: string): Promise<boolean>;
  runWorkflow(workflowId: string, payload?: Record<string, any>): Promise<ExecutionLog>;
  getExecutionHistory(workflowId: string): Promise<ExecutionLog[]>;
}

/**
 * Service contract for Dashboard & Agent telemetry
 */
export interface IMetricsService {
  getDashboardMetrics(): Promise<DashboardMetrics>;
  getAgentPerformance(): Promise<AgentPerformanceMetric[]>;
  getActivityFeed(): Promise<ActivityFeedItem[]>;
}

/**
 * Service contract for Customer Registration & Checkout
 */
export interface IRegistrationService {
  submitRegistration(
    workflowId: string,
    data: RegistrationFormData
  ): Promise<RegistrationSubmission>;
  getRegistrationStatus(submissionId: string): Promise<RegistrationSubmission | null>;
}
