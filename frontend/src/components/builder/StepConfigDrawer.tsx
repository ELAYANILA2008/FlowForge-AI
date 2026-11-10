"use client";

import React, { useState } from "react";
import { X, Save, Sliders, Shield, Mail, CreditCard, UserCheck } from "lucide-react";
import { WorkflowStep } from "@/types/workflow";
import { Button } from "@/components/common/Button";

interface StepConfigDrawerProps {
  step: WorkflowStep | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedStep: WorkflowStep) => void;
}

export const StepConfigDrawer: React.FC<StepConfigDrawerProps> = ({
  step,
  isOpen,
  onClose,
  onSave,
}) => {
  if (!isOpen || !step) return null;

  const [title, setTitle] = useState(step.title);
  const [description, setDescription] = useState(step.description);
  const [capacity, setCapacity] = useState(step.config.capacity || 50);
  const [price, setPrice] = useState(step.config.price || 20);
  const [currency, setCurrency] = useState(step.config.currency || "USD");
  const [emailTemplate, setEmailTemplate] = useState(
    step.config.emailTemplate || "workshop_confirmation_standard"
  );
  const [autoRetry, setAutoRetry] = useState(step.config.autoRetry ?? true);

  const handleSave = () => {
    const updated: WorkflowStep = {
      ...step,
      title,
      description,
      config: {
        ...step.config,
        capacity: Number(capacity),
        price: Number(price),
        currency,
        emailTemplate,
        autoRetry,
      },
    };
    onSave(updated);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl z-10 flex flex-col justify-between h-full overflow-hidden">
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <h3 className="font-semibold text-white text-base">Configure Step Parameters</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Title */}
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Step Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Step Description
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none"
            />
          </div>

          {/* Type Specific Fields */}
          {step.type === "registration" && (
            <div className="space-y-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
                <UserCheck className="w-4 h-4" /> Registration Capacity Limit
              </div>
              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Maximum Available Seats
                </label>
                <input
                  type="number"
                  value={capacity}
                  onChange={(e) => setCapacity(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-indigo-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Once capacity is reached, registration automatically halts with waitlist prompt.
                </p>
              </div>
            </div>
          )}

          {step.type === "payment" && (
            <div className="space-y-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center gap-2 text-sky-400 text-xs font-semibold">
                <CreditCard className="w-4 h-4" /> PayPal Checkout Pricing
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Fee Amount</label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(Number(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Currency</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-indigo-500"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step.type === "email" && (
            <div className="space-y-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center gap-2 text-violet-400 text-xs font-semibold">
                <Mail className="w-4 h-4" /> Email Template Selector
              </div>
              <div>
                <label className="block text-xs text-slate-300 mb-1">Template Preset</label>
                <select
                  value={emailTemplate}
                  onChange={(e) => setEmailTemplate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:border-indigo-500"
                >
                  <option value="workshop_confirmation_standard">
                    Workshop Confirmation + QR Ticket (Standard)
                  </option>
                  <option value="webinar_vip_link">
                    VIP Webinar Link + Calendar Attachment
                  </option>
                  <option value="bootcamp_onboarding">
                    Bootcamp Onboarding & GitHub Access Packet
                  </option>
                </select>
              </div>
            </div>
          )}

          {/* Fault Tolerance & Retries */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
              <Shield className="w-4 h-4" /> Deterministic Execution Safeguards
            </div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRetry}
                onChange={(e) => setAutoRetry(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700"
              />
              <span className="text-xs text-slate-300">
                Enable self-healing retry on transient network drops
              </span>
            </label>
          </div>
        </div>

        {/* Drawer Footer */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between bg-slate-950">
          <Button variant="ghost" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleSave}
            leftIcon={<Save className="w-3.5 h-3.5" />}
          >
            Apply Changes
          </Button>
        </div>
      </div>
    </div>
  );
};
