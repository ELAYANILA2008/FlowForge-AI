import { Workflow, WorkflowStep } from "@/types/workflow";

interface ParseResult {
  title: string;
  description: string;
  capacity: number;
  price: number;
  currency: string;
  paymentProvider: "paypal" | "stripe";
  steps: WorkflowStep[];
  reasoningSteps: string[];
}

export function parsePromptToWorkflow(promptText: string): ParseResult {
  const text = promptText.trim();
  const lower = text.toLowerCase();

  // Extract capacity limit
  let capacity = 50;
  const capacityMatch = text.match(/(\d+)\s*(students|seats|attendees|participants|tickets|people|users)/i);
  if (capacityMatch && capacityMatch[1]) {
    capacity = parseInt(capacityMatch[1], 10);
  }

  // Extract price
  let price = 20;
  let currency = "USD";
  const priceMatch = text.match(/\$(\d+(\.\d{1,2})?)/);
  if (priceMatch && priceMatch[1]) {
    price = parseFloat(priceMatch[1]);
  } else {
    const euroMatch = text.match(/€(\d+(\.\d{1,2})?)/);
    if (euroMatch && euroMatch[1]) {
      price = parseFloat(euroMatch[1]);
      currency = "EUR";
    }
  }

  // Determine title
  let title = "Automated Business Operation";
  if (lower.includes("photography")) {
    title = `Photography Workshop (${capacity} Seats @ $${price})`;
  } else if (lower.includes("webinar") || lower.includes("masterclass")) {
    title = `Masterclass & Webinar Registration Funnel`;
  } else if (lower.includes("bootcamp") || lower.includes("course")) {
    title = `Cohort Bootcamp Registration & Onboarding`;
  } else if (lower.includes("consulting") || lower.includes("coaching")) {
    title = `Consulting Session Booking & Payment Flow`;
  } else {
    const words = text.split(" ").slice(0, 5).join(" ");
    title = words.charAt(0).toUpperCase() + words.slice(1);
  }

  const reasoningSteps = [
    `Extracted operation parameters: capacity = ${capacity} attendees, unit price = ${currency === "USD" ? "$" : currency}${price}.`,
    `Identified customer entry point: Public responsive registration form with capacity guardrails.`,
    `Configured financial transaction layer: PayPal Sandbox/Live integration with instant webhook listener.`,
    `Synthesized risk verification: Automated signature validation and double-spending prevention.`,
    `Constructed fulfillment logic: Transactional confirmation email with personalized QR ticket.`,
    `Linked business intelligence: Real-time telemetry sync with dashboard analytics and seat counters.`,
  ];

  const steps: WorkflowStep[] = [
    {
      id: "step-1",
      order: 1,
      type: "registration",
      title: "Student Registration Portal",
      description: `Generates hosted registration portal with ${capacity} seat limit and realtime reservation lock.`,
      iconName: "UserCheck",
      status: "completed",
      config: {
        capacity: capacity,
        customFields: [
          { label: "Full Name", key: "fullName", type: "text", required: true },
          { label: "Email Address", key: "email", type: "email", required: true },
          { label: "Attendee Notes", key: "notes", type: "text", required: false },
        ],
      },
      metrics: {
        avgExecutionTimeMs: 140,
        successRate: 100.0,
      },
    },
    {
      id: "step-2",
      order: 2,
      type: "payment",
      title: "PayPal Payment Gateway",
      description: `Charges $${price}.00 ${currency} per attendee via secure PayPal modal checkout.`,
      iconName: "CreditCard",
      status: "completed",
      config: {
        price: price,
        currency: currency,
        paymentGateway: "paypal",
      },
      metrics: {
        avgExecutionTimeMs: 420,
        successRate: 99.2,
      },
    },
    {
      id: "step-3",
      order: 3,
      type: "verification",
      title: "Payment Status Verification",
      description: "Cryptographically verifies PayPal order capture and IPN webhook notification.",
      iconName: "ShieldCheck",
      status: "completed",
      config: {
        autoRetry: true,
        timeoutSeconds: 30,
      },
      metrics: {
        avgExecutionTimeMs: 180,
        successRate: 99.8,
      },
    },
    {
      id: "step-4",
      order: 4,
      type: "email",
      title: "Confirmation & Ticket Email",
      description: "Dispatches personalized confirmation email with workshop calendar link and order invoice.",
      iconName: "MailCheck",
      status: "completed",
      config: {
        emailTemplate: "workshop_confirmation_standard",
      },
      metrics: {
        avgExecutionTimeMs: 290,
        successRate: 99.5,
      },
    },
    {
      id: "step-5",
      order: 5,
      type: "analytics",
      title: "Dashboard & Business Telemetry",
      description: "Updates owner metrics: decrements remaining seats, logs revenue, and notifies operator.",
      iconName: "BarChart3",
      status: "completed",
      config: {},
      metrics: {
        avgExecutionTimeMs: 110,
        successRate: 100.0,
      },
    },
  ];

  return {
    title,
    description: `Automated ${capacity}-seat operation charging $${price} via PayPal with instant verification and confirmation emails.`,
    capacity,
    price,
    currency,
    paymentProvider: "paypal",
    steps,
    reasoningSteps,
  };
}

export function createWorkflowFromPrompt(promptText: string): Workflow {
  const parsed = parsePromptToWorkflow(promptText);
  const now = new Date().toISOString();

  return {
    id: `wf-${Date.now().toString(36)}`,
    title: parsed.title,
    description: parsed.description,
    prompt: promptText,
    status: "active",
    createdAt: now,
    updatedAt: now,
    tags: ["AI Generated", "PayPal", "Auto-Operations"],
    stats: {
      totalRuns: 0,
      successfulRuns: 0,
      failedRuns: 0,
      totalRevenue: 0,
      totalRegistrations: 0,
      capacityLimit: parsed.capacity,
      reliabilityScore: 100.0,
      avgRunDurationMs: 1140,
    },
    steps: parsed.steps,
  };
}
