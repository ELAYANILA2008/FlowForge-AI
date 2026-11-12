"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  CheckCircle2,
  CreditCard,
  Sparkles,
  ArrowLeft,
  Smartphone,
  Tablet,
  Monitor,
  ShieldCheck,
  Check,
  RotateCcw,
  Info,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { WorkflowService, RegistrationService } from "@/services/api";
import { Workflow } from "@/types/workflow";

function formatCurrency(amount: number, currencyCode: string = "USD"): string {
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currencyCode.toUpperCase(),
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${currencyCode.toUpperCase()} ${amount.toFixed(2)}`;
  }
}

export default function RegistrationPreviewPage() {
  const params = useParams();
  const workflowId = (params?.id as string) || "wf-photo-001";

  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [deviceView, setDeviceView] = useState<"desktop" | "tablet" | "mobile">("desktop");

  // Registration Form State
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [skillLevel, setSkillLevel] = useState("intermediate");
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [checkoutStep, setCheckoutStep] = useState<"form" | "paypal_modal" | "success">("form");
  const [mockOrderId, setMockOrderId] = useState("");
  const [seatsTaken, setSeatsTaken] = useState(0);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  useEffect(() => {
    async function loadWf() {
      try {
        const wf = await WorkflowService.getWorkflowById(workflowId);
        if (wf) {
          setWorkflow(wf);
          setSeatsTaken(wf.stats?.totalRegistrations ?? 0);
        }
      } catch (e) {
        console.error("Failed to load workflow for preview", e);
      }
    }
    loadWf();
  }, [workflowId]);

  const priceStep = workflow?.steps.find((s) => s.type === "payment");
  const feeAmount = priceStep?.config.price ?? 20;
  const currency = priceStep?.config.currency ?? "USD";
  const capacityStep = workflow?.steps.find((s) => s.type === "registration");
  const seatsTotal = capacityStep?.config.capacity ?? workflow?.stats?.capacityLimit ?? 50;
  const seatsRemaining = Math.max(0, seatsTotal - seatsTaken);
  const isFull = seatsRemaining <= 0;

  const handleStartCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    if (isFull || seatsRemaining <= 0) {
      setPaymentError("Registration is full. No seats remaining.");
      return;
    }
    if (!fullName || !email) return;
    setPaymentError(null);
    setCheckoutStep("paypal_modal");
  };

  const handleSimulatePayment = async () => {
    // Check capacity again before submitting registration
    if (seatsRemaining <= 0 || seatsTaken >= seatsTotal) {
      setPaymentError("Registration is full. No seats remaining to complete this reservation.");
      return;
    }

    setIsSubmitting(true);
    setPaymentError(null);

    try {
      const res = await RegistrationService.submitRegistration(workflow?.id || workflowId, {
        studentName: fullName,
        studentEmail: email,
        experienceLevel: skillLevel as any,
        specialRequests: notes,
      });

      if (res.paymentStatus === "failed") {
        throw new Error("Payment authorization was declined. Please try again.");
      }

      setMockOrderId(res.paypalTransactionId || res.id || `SIM-${Date.now().toString(36).toUpperCase()}`);
      // Never increment beyond capacity
      setSeatsTaken((prev) => Math.min(seatsTotal, prev + 1));
      setCheckoutStep("success");
    } catch (err) {
      console.error("Failed to submit registration", err);
      // Keep user out of success screen, show clear error and allow retry
      const message =
        err instanceof Error
          ? err.message
          : "Registration simulation failed. Please try again.";
      setPaymentError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFullName("");
    setEmail("");
    setNotes("");
    setPaymentError(null);
    setMockOrderId("");
    setCheckoutStep("form");
  };

  const containerWidthClass = {
    desktop: "max-w-4xl",
    tablet: "max-w-2xl",
    mobile: "max-w-md",
  }[deviceView];

  const title = workflow?.title || "Mastering Natural Light & Portraiture Photography";
  const description =
    workflow?.description ||
    "Join award-winning portrait photographer Marcus Vance for an intensive hands-on workshop covering ambient exposure, camera optics, and framing.";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Preview Control Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/builder"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Builder</span>
          </Link>
          <span className="text-slate-700 hidden sm:inline">|</span>
          <span className="text-xs font-mono text-indigo-400 font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Customer Registration Preview
          </span>
        </div>

        {/* Viewport switcher */}
        <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setDeviceView("desktop")}
            className={`p-1.5 rounded transition-colors ${
              deviceView === "desktop"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
            title="Desktop View"
          >
            <Monitor className="w-4 h-4" />
          </button>
          <button
            onClick={() => setDeviceView("tablet")}
            className={`p-1.5 rounded transition-colors ${
              deviceView === "tablet"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
            title="Tablet View"
          >
            <Tablet className="w-4 h-4" />
          </button>
          <button
            onClick={() => setDeviceView("mobile")}
            className={`p-1.5 rounded transition-colors ${
              deviceView === "mobile"
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
            title="Mobile View"
          >
            <Smartphone className="w-4 h-4" />
          </button>
        </div>

        <div className="inline-flex items-center gap-1.5 text-xs text-slate-400 font-mono">
          <Info className="w-3.5 h-3.5 text-indigo-400" />
          <span>Demo Sandbox Simulation</span>
        </div>
      </div>

      {/* Main Preview Container */}
      <div className="flex-1 p-4 sm:p-8 flex justify-center items-start overflow-y-auto">
        <div
          className={`w-full ${containerWidthClass} bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden transition-all duration-300`}
        >
          {/* Header Banner */}
          <div className="relative bg-gradient-to-r from-indigo-900 via-indigo-950 to-slate-950 p-6 sm:p-10 border-b border-slate-800">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <Badge variant="indigo">Official Registration Portal</Badge>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-700 text-xs font-mono">
                <Users className="w-3.5 h-3.5 text-indigo-400" />
                {isFull ? (
                  <span className="text-amber-400 font-bold">Registration Full</span>
                ) : (
                  <span className="text-emerald-400 font-bold">{seatsRemaining} seats left</span>
                )}
                <span className="text-slate-500">({seatsTaken}/{seatsTotal} filled)</span>
              </div>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {title}
            </h1>
            <p className="mt-2 text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              {description}
            </p>

            {/* Event Meta Badges */}
            <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-300 font-medium">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-indigo-400" />
                <span>Upcoming Session · Confirmed Schedule</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-indigo-400" />
                <span>Live Interactive Operational Mesh</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-indigo-400" />
                <span>Virtual HD Stream & In-Person Access</span>
              </div>
            </div>
          </div>

          {/* Form / Checkout Body */}
          <div className="p-6 sm:p-10">
            {checkoutStep === "form" && (
              <form onSubmit={handleStartCheckout} className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-white mb-1">
                    Student Registration & Seat Claim
                  </h3>
                  <p className="text-xs text-slate-400">
                    Provide your information to reserve your seat and proceed to PayPal checkout.
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
                      Full Legal Name *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Elena Rostova"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="e.g. elena@photography.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />
                    <p className="text-[11px] text-slate-500 mt-1">
                      Your admission ticket and access credentials will be simulated for this address.
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
                      Participant Experience Level
                    </label>
                    <select
                      value={skillLevel}
                      onChange={(e) => setSkillLevel(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="beginner">Beginner (Foundational)</option>
                      <option value="intermediate">Intermediate (Practicing / Experienced)</option>
                      <option value="advanced">Advanced / Professional</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5">
                      Specific Questions or Notes (Optional)
                    </label>
                    <textarea
                      rows={2}
                      placeholder="e.g. Inquiries or specific focus topics..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
                    />
                  </div>
                </div>

                {/* Price Summary Breakdown */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Admission Fee</span>
                    <span>{formatCurrency(feeAmount, currency)}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Confirmation Ticket & Verification</span>
                    <span className="text-emerald-400">Included Free</span>
                  </div>
                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-sm font-bold text-white">
                    <span>Total Due Now</span>
                    <span className="text-emerald-400 font-mono text-base">
                      {formatCurrency(feeAmount, currency)}
                    </span>
                  </div>
                </div>

                {/* Registration Full Notice */}
                {isFull && (
                  <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-2.5">
                    <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
                    <span>
                      <strong>Registration Full:</strong> All {seatsTotal} seats for this session are currently claimed.
                    </span>
                  </div>
                )}

                {/* PayPal Checkout Button Placeholder */}
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={isFull}
                    className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-lg transition-all ${
                      isFull
                        ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700 shadow-none"
                        : "bg-[#0070ba] hover:bg-[#005ea6] text-white shadow-blue-900/20"
                    }`}
                  >
                    <CreditCard className="w-4 h-4" />
                    <span>
                      {isFull
                        ? "Registration Full"
                        : `Pay with PayPal (${formatCurrency(feeAmount, currency)})`}
                    </span>
                  </button>
                  <p className="text-[11px] text-center text-slate-500 mt-2 flex items-center justify-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Simulated Sandbox Payment Flow. No actual card charged.
                  </p>
                </div>
              </form>
            )}

            {/* Simulated PayPal Modal */}
            {checkoutStep === "paypal_modal" && (
              <div className="p-6 bg-slate-950 rounded-2xl border border-blue-500/30 text-center space-y-5">
                <div className="w-12 h-12 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center mx-auto">
                  <CreditCard className="w-6 h-6" />
                </div>
                <div>
                  <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-950/80 border border-blue-800 text-[11px] font-mono text-blue-300 mb-2">
                    <Info className="w-3 h-3 text-blue-400" /> Demo Payment Simulation
                  </div>
                  <h3 className="text-base font-bold text-white">
                    Simulate PayPal Order Authorization
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                    Attendee: <strong className="text-slate-200">{fullName}</strong> ({email})
                  </p>
                  <div className="mt-3 text-2xl font-mono font-bold text-emerald-400">
                    {formatCurrency(feeAmount, currency)}
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Demo Mode: This simulates an authorized transaction without charging a real account.
                  </p>
                </div>

                {/* Error message if payment simulation failed */}
                {paymentError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs text-left flex items-start gap-2.5">
                    <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-semibold text-rose-200">Simulation Failed</div>
                      <div className="text-rose-300 mt-0.5">{paymentError}</div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-center gap-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setPaymentError(null);
                      setCheckoutStep("form");
                    }}
                  >
                    Back to Form
                  </Button>
                  <Button
                    variant="primary"
                    size="md"
                    isLoading={isSubmitting}
                    onClick={handleSimulatePayment}
                  >
                    {paymentError ? "Retry Simulation" : "Approve & Verify Payment"}
                  </Button>
                </div>
              </div>
            )}

            {/* Success State */}
            {checkoutStep === "success" && (
              <div className="p-8 bg-slate-950 rounded-2xl border border-emerald-500/30 text-center space-y-5">
                <div className="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto ring-8 ring-emerald-500/10">
                  <Check className="w-7 h-7" />
                </div>
                <div>
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-800 text-[11px] font-mono text-emerald-300 mb-2">
                    <Sparkles className="w-3 h-3 text-emerald-400" /> Demo Simulation Completed
                  </div>
                  <h3 className="text-xl font-bold text-white">
                    Registration & Payment Confirmed
                  </h3>
                  <p className="text-xs text-slate-300 mt-1.5 max-w-md mx-auto">
                    Welcome aboard, <strong>{fullName}</strong>. Your seat has been reserved in this demo simulation (simulated confirmation for <strong>{email}</strong>).
                  </p>
                </div>

                {/* Receipt Card */}
                <div className="max-w-sm mx-auto p-4 rounded-xl bg-slate-900 border border-slate-800 text-left text-xs font-mono space-y-2.5">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
                      Demo Transaction Receipt
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/50">
                      Simulated
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Transaction ID</span>
                    <span className="text-slate-200">{mockOrderId}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Amount Simulated</span>
                    <span className="text-emerald-400 font-bold">
                      {formatCurrency(feeAmount, currency)}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Status</span>
                    <span className="text-teal-400">Simulated / Demo Verified</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Remaining Seats</span>
                    <span className="text-indigo-300">{seatsRemaining} seats</span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
                  Note: This was a simulated demonstration payment. No live PayPal charge was made, and no real webhooks or confirmation emails were dispatched.
                </p>

                <div className="flex items-center justify-center gap-3 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
                  >
                    Register Another Student
                  </Button>
                  <Link href="/dashboard">
                    <Button variant="primary" size="sm">
                      Return to Owner Dashboard
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
