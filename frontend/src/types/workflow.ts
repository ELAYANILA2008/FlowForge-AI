export type StepType =
  | "registration"
  | "payment"
  | "verification"
  | "email"
  | "analytics"
  | "webhook"
  | "custom";

export type StepStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export interface WorkflowStep {
  id: string;
  order: number;
  type: StepType;
  title: string;
  description: string;
  iconName: string;
  status?: StepStatus;
  config: {
    capacity?: number;
    price?: number;
    currency?: string;
    paymentGateway?: "paypal" | "stripe";
    emailTemplate?: string;
    webhookUrl?: string;
    customFields?: { label: string; key: string; type: string; required: boolean }[];
    autoRetry?: boolean;
    timeoutSeconds?: number;
    [key: string]: any;
  };
  metrics?: {
    avgExecutionTimeMs: number;
    successRate: number;
    lastExecutedAt?: string;
  };
}

export type WorkflowStatus = "active" | "draft" | "paused" | "completed" | "failed";

export interface Workflow {
  id: string;
  title: string;
  description: string;
  prompt: string;
  status: WorkflowStatus;
  createdAt: string;
  updatedAt: string;
  steps: WorkflowStep[];
  stats: {
    totalRuns: number;
    successfulRuns: number;
    failedRuns: number;
    totalRevenue: number;
    totalRegistrations: number;
    capacityLimit: number;
    reliabilityScore: number; // e.g. 99.8
    avgRunDurationMs: number;
  };
  tags: string[];
}

export interface ExecutionLog {
  id: string;
  workflowId: string;
  timestamp: string;
  status: "success" | "failed" | "running";
  trigger: "registration_submission" | "manual_test" | "webhook" | "scheduled";
  durationMs: number;
  customer?: {
    name: string;
    email: string;
  };
  stepResults: {
    stepId: string;
    stepTitle: string;
    status: "success" | "failed" | "running" | "skipped";
    durationMs: number;
    message: string;
    payload?: Record<string, any>;
  }[];
}
