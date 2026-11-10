# FlowForge AI – Frontend Architecture & Developer Guide

Frontend module for **FlowForge AI** ("AI That Builds and Runs Business Operations Automatically").

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (Strict type checking)
- **Styling**: Tailwind CSS with custom dark SaaS tokens and glassmorphism utilities
- **Icons**: Lucide React
- **Service Layer**: Pluggable mock and REST adapter (`services/api.ts`)

---

## Directory Structure

```
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
├── next.config.mjs
├── .env.example
├── .env.local
└── src/
    ├── app/
    │   ├── layout.tsx                     # Root SaaS layout, fonts, header/footer
    │   ├── page.tsx                       # High-converting Landing Page
    │   ├── globals.css                    # Tailwind directives and custom utility classes
    │   ├── not-found.tsx                  # Custom 404 page
    │   ├── dashboard/
    │   │   ├── layout.tsx                 # Dashboard shell with sidebar and top navigation
    │   │   ├── page.tsx                   # Business Owner Dashboard Overview
    │   │   ├── builder/
    │   │   │   └── page.tsx               # Interactive AI Workflow Builder
    │   │   ├── workflows/
    │   │   │   ├── page.tsx               # Workflow Management (List, Filter, Search)
    │   │   │   └── [id]/
    │   │   │       └── page.tsx           # Workflow Details & Realtime Execution History
    │   │   └── performance/
    │   │       └── page.tsx               # AI Agent Performance & Quality Metrics
    │   └── preview/
    │       └── [id]/
    │           └── page.tsx               # Customer Registration Page Preview (Standalone + Modal)
    ├── components/
    │   ├── common/                        # Button, Card, Badge, Modal
    │   ├── landing/                       # Navbar, Hero, WorkflowVisualizer, Features, HowItWorks, AgentProof, Pricing, Footer
    │   ├── dashboard/                     # Sidebar, TopNav, MetricCard, ActivityFeed, ExecutionChart
    │   └── builder/                       # NodeCard, StepConfigDrawer, RunSimulationModal
    ├── services/
    │   ├── api.ts                         # Client API adapter (switches between mock and real endpoints)
    │   ├── mockData.ts                    # Realistic demo data for workflows, metrics, and executions
    │   └── workflowGenerator.ts           # Client-side intelligent parser simulating the AI Engine
    └── types/
        ├── workflow.ts                    # Workflow, Step, Node, and Execution schemas
        ├── metrics.ts                     # Dashboard and Agent Performance KPI types
        └── registration.ts                # Customer registration and payment status types
```

---

## Getting Started

### 1. Install Node.js
If not already installed on your system, install Node.js LTS via winget:
```powershell
winget install OpenJS.NodeJS.LTS --source winget --accept-source-agreements --accept-package-agreements --silent
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Start Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

### 4. Build for Production
```bash
npm run build
npm run start
```

---

## Backend API Specification (For Backend & AI Engine Teams)

The frontend expects the following REST API endpoints from the FastAPI backend when `NEXT_PUBLIC_USE_MOCK=false`:

### 1. Workflow Generation
- **Endpoint**: `POST /api/v1/workflows/generate`
- **Request Body**:
  ```json
  {
    "prompt": "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
  }
  ```
- **Response**: Full `Workflow` object with generated `steps`.

### 2. Workflows Collection
- **Endpoint**: `GET /api/v1/workflows`
  - Returns `Workflow[]` list.
- **Endpoint**: `POST /api/v1/workflows`
  - Creates a new `Workflow`.
- **Endpoint**: `GET /api/v1/workflows/{id}`
  - Returns single `Workflow` with details.
- **Endpoint**: `PUT /api/v1/workflows/{id}`
  - Updates workflow configuration.
- **Endpoint**: `POST /api/v1/workflows/{id}/run`
  - Triggers execution and returns `ExecutionLog`.
- **Endpoint**: `GET /api/v1/workflows/{id}/executions`
  - Returns historical `ExecutionLog[]`.

### 3. Business & Agent Metrics
- **Endpoint**: `GET /api/v1/metrics/dashboard`
  - Returns `DashboardMetrics` (KPI counts, 7-day revenue trend, 7-day execution trend).
- **Endpoint**: `GET /api/v1/metrics/agents`
  - Returns `AgentPerformanceMetric[]` (completion rates, latencies, reliability scores).
- **Endpoint**: `GET /api/v1/activity`
  - Returns `ActivityFeedItem[]` (live event stream).
