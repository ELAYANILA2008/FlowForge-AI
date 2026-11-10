import React from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { WorkflowVisualizer } from "@/components/landing/WorkflowVisualizer";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { AgentProof } from "@/components/landing/AgentProof";
import { Pricing } from "@/components/landing/Pricing";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-surface-base">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <WorkflowVisualizer />
        <Features />
        <HowItWorks />
        <AgentProof />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}
