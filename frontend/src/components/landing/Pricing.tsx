import React from "react";
import Link from "next/link";
import { Check, Sparkles } from "lucide-react";
import { Button } from "@/components/common/Button";

export const Pricing: React.FC = () => {
  const plans = [
    {
      name: "Starter",
      tagline: "For solo operators and single workshops",
      price: "$29",
      period: "/month",
      features: [
        "Up to 3 active automated workflows",
        "PayPal checkout integration",
        "Hosted customer registration pages",
        "Automated confirmation email dispatch",
        "Standard execution telemetry",
        "Community support",
      ],
      isPopular: false,
      cta: "Start Free Trial",
    },
    {
      name: "Professional",
      tagline: "For growing businesses & creators",
      price: "$79",
      period: "/month",
      features: [
        "Unlimited active workflows",
        "PayPal & Stripe payment gateways",
        "Custom domains for registration pages",
        "Advanced fraud & IPN verification",
        "Self-healing automated error retry",
        "Full AI agent benchmark analytics",
        "Priority 24/7 operator support",
      ],
      isPopular: true,
      cta: "Launch Pro Workspace",
    },
    {
      name: "Enterprise",
      tagline: "For mission-critical operations",
      price: "$249",
      period: "/month",
      features: [
        "Dedicated LLM router & agent cluster",
        "99.99% execution SLA guarantee",
        "Custom webhook integrations & SSO",
        "High-volume registration queues",
        "Dedicated account engineer",
        "Custom compliance & audit exports",
      ],
      isPopular: false,
      cta: "Contact Enterprise",
    },
  ];

  return (
    <section id="pricing" className="py-24 bg-slate-950 border-t border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 mb-3">
            <span>Transparent Pricing</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Simple, Value-Driven Investment
          </h2>
          <p className="mt-3 text-slate-400 text-base">
            Never pay for wasted AI loops. Pay for verifiable operational execution.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((p, idx) => (
            <div
              key={idx}
              className={`rounded-2xl p-8 flex flex-col justify-between transition-all duration-200 border ${
                p.isPopular
                  ? "bg-slate-900 border-indigo-500 shadow-xl shadow-indigo-500/10 ring-1 ring-indigo-500/50 relative"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
              }`}
            >
              {p.isPopular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-indigo-600 text-[11px] font-semibold tracking-wider uppercase text-white flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Most Popular
                </div>
              )}

              <div>
                <h3 className="text-xl font-bold text-white">{p.name}</h3>
                <p className="text-xs text-slate-400 mt-1 mb-6">{p.tagline}</p>

                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-extrabold text-white font-mono tracking-tight">
                    {p.price}
                  </span>
                  <span className="text-xs text-slate-400">{p.period}</span>
                </div>

                <div className="space-y-3 pt-6 border-t border-slate-800 text-sm">
                  {p.features.map((feat, fIdx) => (
                    <div key={fIdx} className="flex items-start gap-2.5">
                      <Check className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-300 text-xs leading-relaxed">{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-8">
                <Link href="/dashboard/builder">
                  <Button
                    variant={p.isPopular ? "primary" : "secondary"}
                    className="w-full text-sm font-semibold"
                  >
                    {p.cta}
                  </Button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
