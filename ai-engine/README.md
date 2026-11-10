# FlowForge AI - AI Engine Module

The **AI Engine** is responsible for natural language understanding (NLU), business requirement extraction, prompt engineering, allowlisted workflow generation, and schema validation for the FlowForge AI platform.

---

## 1. Module Boundaries

In compliance with project architecture:
- **Scope**: AI Engine handles ONLY instruction parsing, requirements extraction, and validated declarative JSON workflow generation.
- **Workflow Execution**: A separate **Workflow Execution Engine** (developed by the backend team) reads these generated JSON specifications and executes them (handling PayPal API orders, emails, database storage, etc.).
- **No Direct Execution**: The AI Engine does NOT run scripts, does NOT execute payments, and does NOT send emails directly.

---

## 2. Structured Workflow JSON Contract

Every validated workflow returned by the AI Engine conforms to this JSON contract:

```json
{
  "workflow_name": "Photography Workshop",
  "description": "Automated photography workshop registration",
  "trigger": "student_registration",
  "configuration": {
    "capacity": 50,
    "price": 20.0,
    "currency": "USD"
  },
  "steps": [
    {
      "step_id": 1,
      "action": "create_registration_page",
      "parameters": {
        "title": "Photography Workshop",
        "capacity": 50
      }
    },
    {
      "step_id": 2,
      "action": "collect_customer_details",
      "parameters": {
        "fields": ["name", "email"]
      }
    },
    {
      "step_id": 3,
      "action": "create_paypal_order",
      "parameters": {
        "amount": 20.0,
        "currency": "USD"
      }
    },
    {
      "step_id": 4,
      "action": "verify_payment",
      "parameters": {
        "provider": "paypal"
      }
    },
    {
      "step_id": 5,
      "action": "send_confirmation_email",
      "parameters": {
        "template": "workshop_confirmation"
      }
    }
  ],
  "status": "draft"
}
```

### Approved Allowlisted Workflow Actions

The Execution Engine only needs to handle the following allowlisted action names:

| Action Name | Description | Key Parameters |
|---|---|---|
| `create_registration_page` | Event/workshop registration page | `title`, `capacity`, `description` |
| `create_booking_page` | Appointment booking page | `service_name`, `duration_minutes` |
| `create_order_checkout` | Physical/digital product checkout | `product_name`, `price`, `currency` |
| `collect_customer_details` | Collect customer contact information | `fields` (e.g. `["name", "email"]`) |
| `schedule_appointment_slot`| Schedule an appointment slot in calendar | `calendar_id`, `slot_duration` |
| `create_paypal_order` | Initialize PayPal checkout order | `amount`, `currency`, `intent` |
| `verify_payment` | Verify PayPal payment capture | `provider` (`"paypal"`) |
| `send_confirmation_email` | Send email with confirmation/receipt | `template`, `subject` |
| `send_notification` | Send SMS or notification alert | `channel`, `message_template` |

---

## 3. Configuration: OpenAI API Key

The engine supports running in **two modes**:
1. **Mock Mode (Default when no key is set)**: Zero external dependencies required. Simulates the OpenAI LLM deterministically for testing and local development.
2. **Live OpenAI Mode**: Uses the official `openai` Python SDK.

### Setting the API Key

Set the environment variable in your terminal, shell profile, or `.env` file:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-actual-openai-api-key"

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-actual-openai-api-key

# Linux / macOS
export OPENAI_API_KEY="sk-your-actual-openai-api-key"
```

### Optional Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | None | OpenAI secret API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`) |
| `OPENAI_TIMEOUT` | `30.0` | Request timeout in seconds |
| `OPENAI_MAX_RETRIES` | `2` | Max retries on transient connection/rate limit errors |
| `FLOWFORGE_AI_MOCK` | `false` | Force mock mode even if an API key is present (`true`/`1`) |

*Security Note: All API keys are masked in logs (e.g., `sk-...cdef`) and are never written to disk or exposed in error messages.*

---

## 4. How to Run & Test

### Run Self-Test Suite (14 unit and integration tests)
```bash
python ai-engine/test_workflow_generator.py
```
or via the CLI flag:
```bash
python ai-engine/workflow_generator.py --test
```

### Generate a Workflow via CLI
```bash
python ai-engine/workflow_generator.py "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
```

### Python API Integration Example
```python
from workflow_generator import WorkflowGenerator

# Automatically uses OPENAI_API_KEY if present, or falls back to mock mode
generator = WorkflowGenerator()

# 1. Extract requirements only
reqs = generator.extract_requirements(
    "Create an online coding workshop for 100 students. Charge ₹500 per student and send email confirmations."
)
print("Extracted requirements:", reqs)

# 2. Generate full validated workflow
result = generator.generate_workflow(
    "Create an online coding workshop for 100 students. Charge ₹500 per student and send email confirmations."
)

if result.success:
    print("Generated Workflow JSON:")
    print(result.to_json(indent=2))
elif result.clarification_needed:
    print("Information missing. Clarification questions:")
    for q in result.clarification_questions:
        print(f" - {q}")
else:
    print("Errors:", result.errors)
```

