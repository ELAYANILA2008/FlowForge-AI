# FlowForge AI — Backend Service

A high-performance, asynchronous REST backend built with **FastAPI**, **SQLAlchemy 2.x**, and **PostgreSQL** (with local SQLite developer fallback) powering automated operations synthesis, attendee intake, and **PayPal Orders API v2** checkout workflows.

---

## 🚀 Tech Stack

* **Runtime**: Python 3.11+
* **Framework**: FastAPI (Pydantic v2, Starlette)
* **ORM & Database**: SQLAlchemy 2.x (QueuePool, pre-ping), PostgreSQL (psycopg3) / SQLite (local dev & testing)
* **Migrations**: Alembic
* **Security & Auth**: PBKDF2-HMAC-SHA256 password hashing (200,000 rounds), HMAC-SHA256 JWT tokens
* **Financial Calculations**: Python `Decimal` with strict 2-decimal-place quantization (ROUND_HALF_UP)
* **External Integrations**:
  * PayPal Orders API v2 Sandbox (`create_order`, `capture_order`, `get_order_status`, `verify-webhook-signature`)
  * FlowForge AI Engine (`WorkflowGenerator` with offline mock client fallback)

---

## 📁 Architecture & Module Overview

```text
backend/
├── alembic/                      # Database migration scripts
│   ├── env.py                    # Alembic migration environment
│   └── versions/                 # Versioned schema migrations
├── app/
│   ├── core/                     # Core system primitives
│   │   ├── config.py             # Pydantic Settings & environment validation
│   │   ├── exceptions.py         # Domain exceptions & global error handlers
│   │   └── security.py           # PBKDF2 hashing & JWT utilities
│   ├── database/                 # Persistence layer
│   │   ├── base.py               # DeclarativeBase & UUID generator
│   │   ├── connection.py         # Engine factory (PostgreSQL QueuePool / SQLite)
│   │   └── session.py            # SessionLocal, get_db, init_db, reset_db
│   ├── models/                   # SQLAlchemy 2.x data models
│   │   ├── user.py               # User account & credentials
│   │   ├── workflow.py           # Business workflow & DAG configurations
│   │   ├── registration.py       # Customer event & workshop registrations
│   │   ├── payment.py            # Payment records & PayPal tracking
│   │   └── transaction.py        # Immutable financial audit transactions
│   ├── schemas/                  # Pydantic v2 request/response schemas
│   │   ├── user.py               # Auth & registration payloads
│   │   ├── workflow.py           # Workflow CRUD & AI generation schemas
│   │   ├── registration.py       # Customer checkout & registration schemas
│   │   ├── payment.py            # Payment & PayPal Orders v2 schemas
│   │   └── analytics.py          # Dashboard telemetry & agent benchmarks
│   ├── routes/                   # FastAPI route endpoints (/api/v1)
│   │   ├── auth.py               # /auth/register, /auth/login, /auth/token, /auth/me
│   │   ├── workflows.py          # /workflows, /workflows/generate, /workflows/{id}
│   │   ├── registrations.py      # /registration/{id}, /registration/status/{id}
│   │   ├── payments.py           # /payments, /payments/create-order, /payments/capture
│   │   ├── webhooks.py           # /webhooks/paypal (signature verification)
│   │   └── analytics.py          # /metrics/dashboard, /metrics/agents, /activity
│   ├── services/                 # Business logic & integrations
│   │   ├── ai_service.py         # AI Engine adapter
│   │   ├── workflow_service.py   # Workflow CRUD & default step synthesis
│   │   ├── registration_service.py# Overbooking-safe seat allocation
│   │   ├── payment_service.py    # Monetary math & payment state machines
│   │   ├── paypal_service.py     # PayPal Orders v2 client & mock fallback
│   │   └── analytics_service.py  # Multi-currency revenue & agent telemetry
│   └── utils/
│       └── currency.py           # Decimal monetary math (USD, EUR, INR)
├── tests/                        # Automated test suites (66 tests)
├── .env.example                  # Environment configuration template
└── requirements.txt              # Production and dev dependencies
```

---

## ⚙️ Local Setup Instructions

### 1. Prerequisites
* Python 3.11+
* Git
* (Optional) PostgreSQL 15+ (SQLite is supported out-of-the-box for local testing)

### 2. Environment Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the template configuration file:
```powershell
cp .env.example .env
```
Edit `.env` to customize settings:
* For local development without PostgreSQL, leave `DATABASE_URL=sqlite+pysqlite:///./flowforge.db`.
* For local development without PayPal Sandbox credentials, leave `PAYPAL_CLIENT_ID` with the placeholder or empty; the backend automatically runs in offline **Mock PayPal Mode**.

### 4. Database Initialization
```powershell
# Apply Alembic migrations
alembic upgrade head
```
*(In SQLite local development mode, `main.py` also calls `init_db()` automatically on startup).*

### 5. Start Development Server
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation will be available at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔒 Environment Variables Reference

| Variable | Default Value | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Runtime mode (`development` or `production`). |
| `DEBUG` | `true` | Enables verbose SQL logging and stack traces. |
| `PORT` | `8000` | Port for the FastAPI HTTP server. |
| `HOST` | `0.0.0.0` | Bind host address. |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins. |
| `DATABASE_URL` | `postgresql+psycopg://...` | SQLAlchemy connection string (PostgreSQL or SQLite). |
| `SECRET_KEY` | *(dev fallback)* | Secret key for JWT & PBKDF2 salts. (Must be ≥32 chars in production). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT token lifetime (24 hours). |
| `ALGORITHM` | `HS256` | JWT signature algorithm. |
| `OPENAI_API_KEY` | *(empty)* | Optional OpenAI API Key (leave empty for offline Mock AI Engine). |
| `AI_ENGINE_USE_MOCK` | `true` | When true, uses offline deterministic AI mock scenarios. |
| `PAYPAL_CLIENT_ID` | *(placeholder)* | PayPal Sandbox Client ID (uses Mock Provider if empty/placeholder). |
| `PAYPAL_CLIENT_SECRET` | *(placeholder)* | PayPal Sandbox Client Secret. |
| `PAYPAL_BASE_URL` | `https://api-m.sandbox.paypal.com` | Base URL for PayPal REST v2 API. |
| `PAYPAL_WEBHOOK_ID` | *(placeholder)* | PayPal registered Webhook ID for signature verification. |

> **Production Security Guarantee**: When `ENVIRONMENT=production`, the application validates that `SECRET_KEY` is not the development default and has at least 32 characters, raising a startup error if insecure.

---

## 📡 API Endpoints Reference

All endpoints return a standardized JSON envelope matching the frontend's `ApiResponse<T>`:
```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable description",
  "timestamp": "2026-11-12T20:00:00.000000+00:00"
}
```

### 1. Diagnostics
* `GET /`: Service name, version, status, and API links.
* `GET /health` & `GET /api/v1/health`: System uptime, database connection, and integration statuses.

### 2. Authentication (`/api/v1/auth`)
* `POST /api/v1/auth/register`: Register owner account (hashes password via PBKDF2, issues JWT).
* `POST /api/v1/auth/login`: Authenticate with JSON payload (`email`, `password`) and obtain JWT.
* `POST /api/v1/auth/token`: OAuth2 password flow endpoint (`application/x-www-form-urlencoded` with `username` and `password`) powering Swagger UI Authorize modal.
* `GET /api/v1/auth/me`: Retrieve current authenticated user profile via Bearer token.

### 3. Workflows (`/api/v1/workflows`)
* `GET /api/v1/workflows`: List all workflows (supports `?status=active` filter).
* `POST /api/v1/workflows`: Create workflow manually with default pipeline steps.
* `POST /api/v1/workflows/generate`: Generate complete workflow from natural language prompt via AI Engine.
* `GET /api/v1/workflows/{id}`: Retrieve workflow by ID.
* `PUT /api/v1/workflows/{id}`: Update workflow title, capacity, price, currency, or configuration.
* `DELETE /api/v1/workflows/{id}`: Delete workflow (cascades to registrations and payments).
* `PATCH /api/v1/workflows/{id}/status`: Transition workflow lifecycle status (`active`, `draft`, `paused`, `completed`).

### 4. Customer Registrations (`/api/v1/registration`)
* `POST /api/v1/registration/{workflow_id}`: Submit registration. Overbooking-safe with row locks and duplicate email protection.
* `GET /api/v1/registration/status/{submission_id}`: Poll customer registration and payment status.
* `GET /api/v1/registrations/workflow/{workflow_id}`: List all registrations for a workflow (owner only).

### 5. Payments & PayPal Orders API v2 (`/api/v1/payments`)
* `POST /api/v1/payments`: Create payment record with monetary validation.
* `POST /api/v1/payments/create-order`: Initiate official PayPal Orders v2 transaction and obtain approval URL.
* `POST /api/v1/payments/capture/{order_id}`: Server-side capture of approved PayPal order (marks payment & registration as `paid`).
* `GET /api/v1/payments/verify/{order_id}`: Authoritatively query server-side PayPal order status.
* `GET /api/v1/payments/{id}`: Retrieve payment details with transaction audit trail.
* `PATCH /api/v1/payments/{id}/status`: Update payment status.
* `POST /api/v1/payments/{id}/transactions`: Manually record financial transaction audit entry.
* `GET /api/v1/payments/registration/{registration_id}`: List all payments for a registration.

### 6. Webhooks (`/api/v1/webhooks`)
* `POST /api/v1/webhooks/paypal`: Cryptographically verified webhook receiver via PayPal API. Handles `PAYMENT.CAPTURE.COMPLETED` and `CHECKOUT.ORDER.APPROVED` with idempotency guards.

### 7. Dashboard Metrics & Telemetry (`/api/v1/metrics`, `/api/v1/activity`)
* `GET /api/v1/metrics/dashboard`: Overall operational KPIs, task completion rates, 7-day trends, and segregated revenues (`totalRevenueUsd`, `totalRevenueInr`, `totalRevenueEur`).
* `GET /api/v1/metrics/agents`: Real-time benchmark telemetry for Workflow Synthesis, PayPal Operations, and Registration Gatekeeper agents.
* `GET /api/v1/activity`: Unified chronological operational activity stream.

---

## 💰 Financial Precision Rules

FlowForge AI enforces strict financial integrity:
1. **Decimal Precision**: All prices, fee computations, and revenue aggregations use Python `Decimal` quantized to `0.01` with `ROUND_HALF_UP`. Binary floating-point representation bugs are prevented.
2. **Supported Currencies**: `USD`, `EUR`, and `INR`. Unsupported currencies are rejected.
3. **No Currency Mixing**: Currencies are strictly kept in isolated buckets (`totalRevenueUsd`, `totalRevenueInr`, `totalRevenueEur`). Different currencies are never combined into a single sum without an explicit exchange rate conversion.
4. **Authoritative Capture Rule**: A payment is **never** marked as `paid` based on client claims; only server-verified PayPal capture confirmations (`status == "COMPLETED"`) trigger the `paid` state.

---

## 🧪 Testing

Execute the comprehensive automated test suite (66 tests):
```powershell
python -m pytest backend/tests -v
```

### Test Suite Structure
* `tests/test_health.py` (5 tests): App startup, health endpoints, CORS, currency utilities.
* `tests/test_database.py` (5 tests): User creation, unique constraints, workflow cascade, capacity enforcement, audit trail.
* `tests/test_auth.py` (13 tests): OAuth2 password flow, /token form-urlencoded generation, FastAPI TestClient integration, invalid credentials rejection, /me profile lookup, token scheme configuration.
* `tests/test_workflows.py` (12 tests): User registration, JWT login, profile lookup, workflow CRUD, status transitions.
* `tests/test_ai_integration.py` (6 tests): Natural language prompt synthesis, multi-currency price parsing, safety guards.
* `tests/test_payments.py` (11 tests): Decimal validation, currency normalization, negative amount rejection, status updates.
* `tests/test_paypal.py` (9 tests): PayPal OAuth2 token caching, Orders v2 creation, capture validation, webhook signature verification, mock provider fallback.
* `tests/test_analytics.py` (5 tests): Multi-currency segregated revenues, agent performance telemetry, activity feeds.

