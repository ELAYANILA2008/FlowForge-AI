"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  Sparkles,
  CreditCard,
  UserCheck,
  CheckCircle2,
  XCircle,
  Gauge,
  ArrowRight,
  ExternalLink,
  Play,
  TrendingUp,
} from "lucide-react";
import { TopNav } from "@/components/dashboard/TopNav";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { ExecutionChart } from "@/components/dashboard/ExecutionChart";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { MetricsService, WorkflowService } from "@/services/api";
import { DashboardMetrics, ActivityFeedItem } from "@/types/metrics";
import { Workflow } from "@/types/workflow";

export default function DashboardOverviewPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [activity, setActivity] = useState<ActivityFeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, wf, act] = await Promise.all([
          MetricsService.getDashboardMetrics(),
          WorkflowService.getAllWorkflows(),
          MetricsService.getActivityFeed(),
        ]);
        setMetrics(m);
        setWorkflows(wf);
        setActivity(act);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !metrics) {
    return (
      <div className="flex-1 flex flex-col">
        <TopNav title="Dashboard Overview" subtitle="Business telemetry & operations console" />
        <div className="p-8 flex items-center justify-center flex-1">
          <div className="inline-flex items-center gap-2 text-indigo-400 text-sm font-mono animate-pulse">
            <Sparkles className="w-4 h-4" /> Loading operations telemetry...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      <TopNav
        title="Business Operations Dashboard"
        subtitle="Autonomous workflow execution, PayPal revenues, and task quality indicators"
      />

      <main className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Quick Action Banner */}
        <div className="bg-gradient-to-r from-indigo-900/40 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xl">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-mono font-medium">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              <span>FlowForge AI Engine Online</span>
            </div>
            <h2 className="text-xl font-bold text-white">
              Ready to automate your next business operation?
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
              Type your requirement in plain English. FlowForge AI will generate customer forms, configure PayPal gateways, and execute the flow.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/preview/wf-photo-001">
              <Button variant="secondary" size="sm" rightIcon={<ExternalLink className="w-3.5 h-3.5" />}>
                Preview Live Form
              </Button>
            </Link>
            <Link href="/dashboard/builder">
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Sparkles className="w-3.5 h-3.5" />}
              >
                Create with AI
              </Button>
            </Link>
          </div>
        </div>

        {/* 6 Core Business KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <MetricCard
            label="Total Workflows"
            value={metrics.totalWorkflows}
            subtitle={`${metrics.activeWorkflows} active operations`}
            change="+2 this week"
            icon={<Layers className="w-4 h-4" />}
            color="indigo"
          />
          <MetricCard
            label="Active Operations"
            value={metrics.activeWorkflows}
            subtitle="Running autonomously"
            icon={<Sparkles className="w-4 h-4" />}
            color="cyan"
          />
          <MetricCard
            label="Successful Tasks"
            value={metrics.successfulExecutions}
            subtitle="Completed with receipt"
            change={`${metrics.overallTaskCompletionRate}% quality`}
            icon={<CheckCircle2 className="w-4 h-4" />}
            color="emerald"
          />
          <MetricCard
            label="Failed Tasks"
            value={metrics.failedExecutions}
            subtitle="Recovered via retry"
            trend="down"
            change="1.1% error rate"
            icon={<XCircle className="w-4 h-4" />}
            color="rose"
          />
          <MetricCard
            label="Registrations"
            value={metrics.totalRegistrations}
            subtitle="Customer seats claimed"
            change="+90 this week"
            icon={<UserCheck className="w-4 h-4" />}
            color="indigo"
          />
          <MetricCard
            label="PayPal Revenue (USD)"
            value={`$${metrics.totalRevenueUsd.toLocaleString()}`}
            subtitle="US Dollar"
            change="+18.4% vol"
            icon={<CreditCard className="w-4 h-4" />}
            color="emerald"
          />

          <MetricCard
            label="PayPal Revenue (INR)"
            value={`₹${metrics.totalRevenueInr.toLocaleString("en-IN")}`}
            subtitle="Indian Rupee"
            change="INR"
            icon={<CreditCard className="w-4 h-4" />}
            color="indigo"
          />

          <MetricCard
            label="PayPal Revenue (EUR)"
            value={`€${metrics.totalRevenueEur.toLocaleString("de-DE")}`}
            subtitle="Euro"
            change="EUR"
            icon={<CreditCard className="w-4 h-4" />}
            color="cyan"
          />
        </div>

        {/* Charts and Live Stream Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <ExecutionChart
              revenueTrend={metrics.revenueTrend}
              executionTrend={metrics.executionTrend}
            />
          </div>
          <div>
            <ActivityFeed items={activity} />
          </div>
        </div>

        {/* Active Workflows Overview Table / Cards */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-sm font-semibold text-white">Active Business Workflows</h3>
              <p className="text-xs text-slate-400">Currently executing operations and their live status</p>
            </div>
            <Link
              href="/dashboard/workflows"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1"
            >
              Manage all workflows <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {workflows.slice(0, 3).map((wf) => (
              <div
                key={wf.id}
                className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge variant={wf.status === "active" ? "active" : "paused"} dot>
                      {wf.status.toUpperCase()}
                    </Badge>
                    <span className="text-sm font-semibold text-white">{wf.title}</span>
                  </div>
                  <p className="text-xs text-slate-400 max-w-xl line-clamp-1">
                    {wf.description}
                  </p>
                </div>

                <div className="flex items-center gap-6 text-xs text-slate-400">
                  <div className="text-right">
                    <div className="font-mono text-emerald-400 font-bold">
                      ${wf.stats.totalRevenue.toLocaleString()}
                    </div>
                    <div className="text-[10px]">
                      {wf.stats.totalRegistrations}/{wf.stats.capacityLimit} seats
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="font-mono text-slate-200 font-medium">
                      {wf.stats.reliabilityScore}%
                    </div>
                    <div className="text-[10px]">Reliability</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link href={`/preview/${wf.id}`}>
                      <Button variant="ghost" size="sm">
                        Preview
                      </Button>
                    </Link>
                    <Link href={`/dashboard/workflows/${wf.id}`}>
                      <Button variant="secondary" size="sm">
                        Details
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
