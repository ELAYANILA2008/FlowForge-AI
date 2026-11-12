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

interface ExtractedPrice {
  price: number;
  currency: string;
}

function getCurrencySymbol(currency: string): string {
  switch (currency.toUpperCase()) {
    case "INR":
      return "₹";
    case "EUR":
      return "€";
    case "USD":
    default:
      return "$";
  }
}

function extractWorkshopTopic(text: string): string {
  const clean = text
    .replace(/^(?:create|organize|set\s*up|host|run|start|launch)\s+/i, "")
    .replace(/^(?:my|our|an?|the|online|virtual|live)\s+/i, "")
    .replace(/^(?:my|our|an?|the|online|virtual|live)\s+/i, "");

  const match = clean.match(/^(.+?)\s+workshop\b/i);
  if (match && match[1]) {
    const raw = match[1].trim();
    const ignore = new Set([
      "a",
      "an",
      "the",
      "my",
      "our",
      "this",
      "new",
      "interactive",
      "virtual",
      "live",
      "offline",
      "annual",
      "online",
    ]);
    if (!ignore.has(raw.toLowerCase())) {
      return raw
        .split(/\s+/)
        .map((w) =>
          w.toUpperCase() === w && w.length > 1
            ? w
            : w.charAt(0).toUpperCase() + w.slice(1)
        )
        .join(" ");
    }
  }
  return "";
}

function extractPriceAndCurrency(text: string): ExtractedPrice {
  // 1. INR: ₹500, Rs. 500, Rs 500, INR 500, 500 INR, 500 rupees, 500₹
  const inrPrefix = text.match(/(?:₹|Rs\.?|INR)\s*(\d+(?:\.\d+)?)/i);
  if (inrPrefix && inrPrefix[1]) {
    return { price: parseFloat(inrPrefix[1]), currency: "INR" };
  }
  const inrSuffix = text.match(/(\d+(?:\.\d+)?)\s*(?:₹|INR\b|rupees?\b|Rs\.?)/i);
  if (inrSuffix && inrSuffix[1]) {
    return { price: parseFloat(inrSuffix[1]), currency: "INR" };
  }

  // 2. EUR: €30, EUR 30, 30 EUR, 30 euros, 30€
  const eurPrefix = text.match(/(?:€|EUR)\s*(\d+(?:\.\d+)?)/i);
  if (eurPrefix && eurPrefix[1]) {
    return { price: parseFloat(eurPrefix[1]), currency: "EUR" };
  }
  const eurSuffix = text.match(/(\d+(?:\.\d+)?)\s*(?:€|EUR\b|euros?\b)/i);
  if (eurSuffix && eurSuffix[1]) {
    return { price: parseFloat(eurSuffix[1]), currency: "EUR" };
  }

  // 3. USD: $20, USD 20, 20 USD, 20 dollars, 20$
  const usdPrefix = text.match(/(?:\$|USD)\s*(\d+(?:\.\d+)?)/i);
  if (usdPrefix && usdPrefix[1]) {
    return { price: parseFloat(usdPrefix[1]), currency: "USD" };
  }
  const usdSuffix = text.match(/(\d+(?:\.\d+)?)\s*(?:\$|USD\b|dollars?\b)/i);
  if (usdSuffix && usdSuffix[1]) {
    return { price: parseFloat(usdSuffix[1]), currency: "USD" };
  }

  // 4. Generic price when price is specified without currency
  const genericPrice = text.match(/(?:charge|price|fee|cost)\s+(?:of\s+)?(\d+(?:\.\d+)?)/i);
  if (genericPrice && genericPrice[1]) {
    return { price: parseFloat(genericPrice[1]), currency: "USD" };
  }

  // 5. Default when no price is specified: 20 USD
  return { price: 20, currency: "USD" };
}

export function parsePromptToWorkflow(promptText: string): ParseResult {
  const text = promptText.trim();
  const lower = text.toLowerCase();

  // Extract capacity limit (default 50)
  let capacity = 50;
  const capacityMatch = text.match(
    /(\d+)\s*(students|seats|attendees|participants|tickets|people|users)/i
  );
  if (capacityMatch && capacityMatch[1]) {
    capacity = parseInt(capacityMatch[1], 10);
  }

  // Single source of truth for price and currency
  const { price, currency } = extractPriceAndCurrency(text);
  const currencySymbol = getCurrencySymbol(currency);
  const displayPrice = Number.isInteger(price) ? `${price}` : price.toFixed(2);

  // Workflow title detection
  let title = "Automated Business Operation";

    // 1. Python Workshop (independent condition)
    if (/\bpython\b/i.test(text)) {
      title = `Python Workshop (${capacity} Seats @ ${currencySymbol}${displayPrice})`;
    } else if (/\bphotography\b/i.test(text)) {
      // 2. Photography Workshop (independent condition)
      title = `Photography Workshop (${capacity} Seats @ ${currencySymbol}${displayPrice})`;
    } else if (/\bworkshop\b/i.test(text)) {
      // 3. Other named workshops
      const topic = extractWorkshopTopic(text);
      if (topic) {
        title = `${topic} Workshop (${capacity} Seats @ ${currencySymbol}${displayPrice})`;
      } else {
        title = `Interactive Workshop (${capacity} Seats @ ${currencySymbol}${displayPrice})`;
      }
    } else if (lower.includes("webinar") || lower.includes("masterclass")) {
      // 4. Webinar / Masterclass
      title = `Masterclass & Webinar Registration Funnel`;
    } else if (lower.includes("bootcamp") || lower.includes("course")) {
      // 5. Bootcamp / Course
      title = `Cohort Bootcamp Registration & Onboarding`;
    } else if (lower.includes("consulting") || lower.includes("coaching")) {
      // 6. Consulting / Coaching
      title = `Consulting Session Booking & Payment Flow`;
    } else {
      // 7. Generic business operations
      const words = text.split(" ").slice(0, 5).join(" ");
      title = words.charAt(0).toUpperCase() + words.slice(1);
    }

    const reasoningSteps = [
      `Extracted operation parameters: capacity = ${capacity} attendees, unit price = ${currencySymbol}${displayPrice}.`,
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
        description: `Charges ${currencySymbol}${displayPrice} per attendee via secure PayPal modal checkout.`,
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
      description: `Automated ${capacity}-seat operation charging ${currencySymbol}${displayPrice} via PayPal with instant verification and confirmation emails.`,
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
