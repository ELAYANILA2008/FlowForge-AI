export interface DashboardMetrics {
  totalWorkflows: number;
  activeWorkflows: number;
  successfulExecutions: number;
  failedExecutions: number;
  totalRegistrations: number;
  totalRevenueUsd: number;
  totalRevenueInr: number;
  totalRevenueEur: number;
  overallTaskCompletionRate: number; // e.g. 99.4%
  avgExecutionTimeSeconds: number; // e.g. 1.34s
  systemReliabilityScore: number; // e.g. 99.9%
  revenueTrend: { date: string; amount: number; registrations: number }[];
  executionTrend: { date: string; successful: number; failed: number }[];
}

export interface AgentPerformanceMetric {
  id: string;
  name: string;
  role: string;
  model: string;
  taskCompletionRate: number; // e.g. 99.6%
  workflowSuccessRate: number; // e.g. 98.9%
  avgExecutionTimeMs: number;
  reliabilityScore: number;
  totalTasksProcessed: number;
  failedTaskCount: number;
  recoveryRate: number; // self-healing percentage
  status: "optimal" | "monitoring" | "degraded";
  lastBenchmarkedAt: string;
}

export interface ActivityFeedItem {
  id: string;
  workflowId: string;
  workflowTitle: string;
  type: "registration" | "payment" | "email" | "error" | "created";
  title: string;
  description: string;
  timestamp: string;
  amount?: number;
  status: "success" | "pending" | "failed";
}
