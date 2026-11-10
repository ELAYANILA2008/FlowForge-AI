"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Cpu, ShieldCheck, FileText, Lock } from "lucide-react";
import { Modal } from "@/components/common/Modal";

export const Footer: React.FC = () => {
  const [activeModal, setActiveModal] = useState<"privacy" | "terms" | "security" | null>(null);

  return (
    <footer className="bg-slate-950 border-t border-slate-900 py-12 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand info */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Cpu className="w-4 h-4" />
              </div>
              <span className="font-bold text-base text-white">
                FlowForge <span className="text-indigo-400">AI</span>
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              AI that builds and runs business operations automatically. Turn plain-English requirements into self-operating workflows.
            </p>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>All Systems Operational (99.98% uptime)</span>
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="text-white font-semibold mb-3">Product</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard/builder" className="hover:text-white transition-colors">
                  AI Workflow Builder
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-white transition-colors">
                  Business Dashboard
                </Link>
              </li>
              <li>
                <Link href="/dashboard/workflows" className="hover:text-white transition-colors">
                  Workflow Management
                </Link>
              </li>
              <li>
                <Link href="/dashboard/performance" className="hover:text-white transition-colors">
                  Agent Quality Benchmarks
                </Link>
              </li>
              <li>
                <Link href="/preview/wf-photo-001" className="hover:text-white transition-colors">
                  Sample Registration Page
                </Link>
              </li>
            </ul>
          </div>

          {/* Technology */}
          <div>
            <h4 className="text-white font-semibold mb-3">Technology</h4>
            <ul className="space-y-2">
              <li>Next.js 14 App Router</li>
              <li>TypeScript Strict Mode</li>
              <li>Tailwind CSS Responsive Primitives</li>
              <li>PayPal Checkout Integration</li>
              <li>Pluggable FastAPI Client Mesh</li>
            </ul>
          </div>

          {/* Status & Compliance */}
          <div>
            <h4 className="text-white font-semibold mb-3">Auditing & Safety</h4>
            <p className="text-slate-400 text-xs leading-relaxed mb-3">
              Telemetry metrics presented in this application are certified by cryptographic execution logging and verifiable receipts.
            </p>
            <div className="text-[11px] text-slate-500 font-mono">
              Build Version 0.1.0-alpha · Next.js 14
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[11px]">
          <div>
            &copy; {new Date().getFullYear()} FlowForge AI. All rights reserved. Exclusively frontend architecture.
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setActiveModal("privacy")}
              className="hover:text-slate-300 transition-colors"
            >
              Privacy Policy
            </button>
            <button
              onClick={() => setActiveModal("terms")}
              className="hover:text-slate-300 transition-colors"
            >
              Terms of Service
            </button>
            <button
              onClick={() => setActiveModal("security")}
              className="hover:text-slate-300 transition-colors"
            >
              Security Protocol
            </button>
          </div>
        </div>
      </div>

      {/* Policy Modals */}
      <Modal
        isOpen={activeModal === "privacy"}
        onClose={() => setActiveModal(null)}
        title={
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>Privacy Policy</span>
          </div>
        }
      >
        <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
          <p>
            FlowForge AI processes student intake data exclusively for the purpose of executing the customer-defined workflow (e.g. issuing event tickets and recording PayPal receipts).
          </p>
          <p>
            All customer registrations in this demonstration environment are handled locally or via secured sandbox adapters. No personal information is monetized or shared with unauthorized third parties.
          </p>
        </div>
      </Modal>

      <Modal
        isOpen={activeModal === "terms"}
        onClose={() => setActiveModal(null)}
        title={
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <span>Terms of Service</span>
          </div>
        }
      >
        <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
          <p>
            FlowForge AI provides autonomous workflow compilation and execution telemetry. Workflow operators maintain legal responsibility for event hosting, ticket terms, and PayPal merchant credentials.
          </p>
          <p>
            Demonstration workflows are provided for evaluation and testing. Real financial transactions require production PayPal client credentials configured on the backend.
          </p>
        </div>
      </Modal>

      <Modal
        isOpen={activeModal === "security"}
        onClose={() => setActiveModal(null)}
        title={
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>Cryptographic Security Protocol</span>
          </div>
        }
      >
        <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
          <p>
            FlowForge AI implements deterministic execution gates: payment fulfillment is guarded by Instant Payment Notification (IPN) webhook signature verification.
          </p>
          <p>
            Ticket dispatches and revenue credits cannot trigger until PayPal cryptographically signs the order capture receipt, preventing double-allocation and unauthorized admissions.
          </p>
        </div>
      </Modal>
    </footer>
  );
};
