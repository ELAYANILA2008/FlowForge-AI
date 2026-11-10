import { IWorkflowService, IMetricsService, IRegistrationService } from "@/types/api";
import {
  MockWorkflowService,
  MockMetricsService,
  MockRegistrationService,
} from "./mockAdapter";
import {
  HttpWorkflowService,
  HttpMetricsService,
  HttpRegistrationService,
} from "./httpAdapter";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false";

/**
 * Primary Workflow Service:
 * Delegates to MockAdapter (default) or HttpAdapter (when NEXT_PUBLIC_USE_MOCK=false)
 */
export const WorkflowService: IWorkflowService = USE_MOCK
  ? MockWorkflowService
  : HttpWorkflowService;

/**
 * Primary Metrics Service:
 * Telemetry and agent benchmarks
 */
export const MetricsService: IMetricsService = USE_MOCK
  ? MockMetricsService
  : HttpMetricsService;

/**
 * Primary Registration Service:
 * Customer intake and simulated payments
 */
export const RegistrationService: IRegistrationService = USE_MOCK
  ? MockRegistrationService
  : HttpRegistrationService;

export const isDemonstrationMode = USE_MOCK;
