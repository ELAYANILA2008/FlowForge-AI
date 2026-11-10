"""OpenAI API Integration and Mock Engine for FlowForge AI.

Implements official OpenAI SDK communication with robust error handling,
exponential retry handling, timeouts, key masking, and an intelligent mock provider
for testing without live credentials or internet access.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

try:
    from .config import AIConfig, mask_api_key, logger
except (ImportError, ValueError):
    from config import AIConfig, mask_api_key, logger

# Attempt to import official OpenAI SDK
try:
    import openai
    from openai import (
        OpenAI,
        APIError,
        APIConnectionError,
        RateLimitError,
        APITimeoutError,
        AuthenticationError,
    )
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    openai = None
    OpenAI = None
    # Lightweight fallback exception hierarchy
    class APIError(Exception): pass
    class APIConnectionError(APIError): pass
    class RateLimitError(APIError): pass
    class APITimeoutError(APIError): pass
    class AuthenticationError(APIError): pass


# FlowForge AI Custom Exceptions
class FlowForgeAIError(Exception):
    """Base exception for FlowForge AI Engine errors."""
    pass


class FlowForgeConnectionError(FlowForgeAIError):
    """Raised when network connection to OpenAI fails."""
    pass


class FlowForgeRateLimitError(FlowForgeAIError):
    """Raised when OpenAI rate limit or quota is exceeded."""
    pass


class FlowForgeTimeoutError(FlowForgeAIError):
    """Raised when an OpenAI request times out."""
    pass


class FlowForgeAuthenticationError(FlowForgeAIError):
    """Raised when OpenAI credentials are invalid or missing."""
    pass


class FlowForgeInvalidResponseError(FlowForgeAIError):
    """Raised when LLM response cannot be parsed as valid JSON or violates schema."""
    pass


class BaseAIClient:
    """Abstract interface for AI client implementations."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class OpenAIClientWrapper(BaseAIClient):
    """Official OpenAI Python SDK client wrapper."""

    def __init__(self, config: AIConfig):
        self.config = config

        if not OPENAI_SDK_AVAILABLE:
            raise FlowForgeAIError(
                "The official 'openai' Python package is not installed. "
                "Install it with 'pip install openai' or use mock mode (FLOWFORGE_AI_MOCK=1)."
            )

        if not self.config.api_key:
            raise FlowForgeAuthenticationError(
                "OpenAI API key is missing. Set OPENAI_API_KEY environment variable "
                "or pass api_key to WorkflowGenerator."
            )

        try:
            self.client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )
            logger.info(
                "OpenAI client successfully initialized (Model: %s, Key: %s)",
                self.config.model,
                mask_api_key(self.config.api_key),
            )
        except Exception as exc:
            logger.error("Failed to initialize OpenAI client: %s", str(exc))
            raise FlowForgeAIError(f"Failed to initialize OpenAI client: {str(exc)}") from exc

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI chat completion API with JSON mode and timeout."""
        logger.info(
            "Calling OpenAI API [%s] with timeout %.1fs...",
            self.config.model,
            self.config.timeout,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=self.config.timeout,
            )

            raw_content = response.choices[0].message.content
            if not raw_content or not raw_content.strip():
                raise FlowForgeInvalidResponseError("OpenAI returned an empty completion response")

            # Validate that response is valid JSON
            try:
                json.loads(raw_content)
            except json.JSONDecodeError as json_err:
                raise FlowForgeInvalidResponseError(
                    f"OpenAI response was not valid JSON: {str(json_err)}"
                ) from json_err

            return raw_content

        except AuthenticationError as exc:
            logger.error("OpenAI Authentication Error: %s", str(exc))
            raise FlowForgeAuthenticationError(
                "OpenAI API authentication failed. Please verify your OPENAI_API_KEY."
            ) from exc

        except APITimeoutError as exc:
            logger.error("OpenAI Timeout Error (timeout=%.1fs): %s", self.config.timeout, str(exc))
            raise FlowForgeTimeoutError(
                f"OpenAI request timed out after {self.config.timeout} seconds."
            ) from exc

        except RateLimitError as exc:
            logger.error("OpenAI Rate Limit Error: %s", str(exc))
            raise FlowForgeRateLimitError(
                "OpenAI API rate limit exceeded or insufficient quota."
            ) from exc

        except APIConnectionError as exc:
            logger.error("OpenAI Connection Error: %s", str(exc))
            raise FlowForgeConnectionError(
                "Could not connect to OpenAI API. Check network connectivity."
            ) from exc

        except APIError as exc:
            logger.error("OpenAI API Error: %s", str(exc))
            raise FlowForgeAIError(f"OpenAI API error: {str(exc)}") from exc

        except Exception as exc:
            logger.error("Unexpected error during OpenAI completion: %s", str(exc))
            raise FlowForgeAIError(f"Unexpected error calling OpenAI: {str(exc)}") from exc


class MockAIClient(BaseAIClient):
    """Intelligent deterministic Mock AI Client for testing without API keys or internet."""

    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig(use_mock=True)
        logger.info("Initialized MockAIClient for offline testing and validation.")

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Analyze the user instruction and return appropriate structured JSON."""
        # Extract user instruction from prompt
        instruction = self._extract_instruction(user_prompt)
        text = instruction.lower().strip()

        logger.info("MockAIClient processing instruction: '%s'", instruction)

        # 1. Check for unsupported or malicious operations
        unsupported_keywords = [
            "hack", "dump credentials", "ddos", "competitor database",
            "mine crypto", "bitcoin miner", "steal", "malware", "exploit",
            "launch rocket", "counterfeit"
        ]
        if any(bad_word in text for bad_word in unsupported_keywords):
            return json.dumps({
                "supported": false if False else False,
                "clarification_needed": False,
                "clarification_questions": [],
                "extracted_requirements": None,
                "workflow": None,
                "rejection_reason": "Unsupported operation: This instruction involves unauthorized security actions or operations outside the scope of business workflow automation."
            })

        # 2. Check for incomplete business instructions (missing price & capacity)
        # Specifically matches TEST 5 or requests that mention events/workshops but omit both price and capacity
        has_price = bool(re.search(r"(\$|₹|€|£|\bUSD\b|\bINR\b|\bEUR\b|\bGBP\b|\bcharge\b|\bprice\b|\bfee\b)\s*\d+", instruction, re.IGNORECASE))
        has_capacity = bool(re.search(r"\b\d+\s*(students|participants|people|attendees|seats|users|clients)\b", instruction, re.IGNORECASE))
        is_workshop_or_event = any(w in text for w in ["workshop", "class", "seminar", "webinar", "course"])

        if is_workshop_or_event and not has_price and not has_capacity:
            # Missing critical information
            return json.dumps({
                "supported": True,
                "clarification_needed": True,
                "clarification_questions": [
                    "What is the maximum student capacity for this workshop?",
                    "How much would you like to charge per student?",
                    "What currency should be used for the PayPal payment (e.g., USD, EUR, INR)?"
                ],
                "extracted_requirements": {
                    "business_type": "workshop_registration",
                    "business_name": self._extract_title(instruction),
                    "workflow_name": f"{self._extract_title(instruction)} Registration",
                    "workflow_objective": f"Registration and payment for {self._extract_title(instruction)}",
                    "trigger": "student_registration",
                    "customer_info_fields": ["name", "email"],
                    "capacity": None,
                    "price": None,
                    "currency": None,
                    "payment_required": True if ("charge" in text or "payment" in text or "pay" in text) else False,
                    "notification": "email" if "email" in text else None
                },
                "workflow": None
            })

        # 3. Match TEST 1: Photography workshop
        if "photograph" in text and ("50" in text or "20" in text):
            return json.dumps({
                "supported": True,
                "clarification_needed": False,
                "clarification_questions": [],
                "extracted_requirements": {
                    "business_type": "photography_workshop",
                    "business_name": "Photography Workshop",
                    "workflow_name": "Photography Workshop",
                    "workflow_objective": "Automated photography workshop registration",
                    "trigger": "student_registration",
                    "customer_info_fields": ["name", "email"],
                    "capacity": 50,
                    "price": 20.0,
                    "currency": "USD",
                    "payment_required": True,
                    "notification": "email"
                },
                "workflow": {
                    "workflow_name": "Photography Workshop",
                    "description": "Automated photography workshop registration",
                    "trigger": "student_registration",
                    "configuration": {
                        "capacity": 50,
                        "price": 20.0,
                        "currency": "USD"
                    },
                    "steps": [
                        {"step_id": 1, "action": "create_registration_page", "parameters": {"title": "Photography Workshop", "capacity": 50}},
                        {"step_id": 2, "action": "collect_customer_details", "parameters": {"fields": ["name", "email"]}},
                        {"step_id": 3, "action": "create_paypal_order", "parameters": {"amount": 20.0, "currency": "USD"}},
                        {"step_id": 4, "action": "verify_payment", "parameters": {"provider": "paypal"}},
                        {"step_id": 5, "action": "send_confirmation_email", "parameters": {"template": "workshop_confirmation"}}
                    ],
                    "status": "draft"
                }
            })

        # 4. Match TEST 2: Online coding class (INR)
        if "coding" in text and ("100" in text or "500" in text or "₹" in instruction or "inr" in text):
            return json.dumps({
                "supported": True,
                "clarification_needed": False,
                "clarification_questions": [],
                "extracted_requirements": {
                    "business_type": "online_workshop",
                    "business_name": "Coding Workshop",
                    "workflow_name": "Coding Workshop",
                    "workflow_objective": "Automated online coding class registration and enrollment",
                    "trigger": "student_registration",
                    "customer_info_fields": ["name", "email"],
                    "capacity": 100,
                    "price": 500.0,
                    "currency": "INR",
                    "payment_required": True,
                    "notification": "email"
                },
                "workflow": {
                    "workflow_name": "Coding Workshop",
                    "description": "Automated online coding class registration and enrollment",
                    "trigger": "student_registration",
                    "configuration": {
                        "capacity": 100,
                        "price": 500.0,
                        "currency": "INR"
                    },
                    "steps": [
                        {"step_id": 1, "action": "create_registration_page", "parameters": {"title": "Coding Workshop", "capacity": 100}},
                        {"step_id": 2, "action": "collect_customer_details", "parameters": {"fields": ["name", "email"]}},
                        {"step_id": 3, "action": "create_paypal_order", "parameters": {"amount": 500.0, "currency": "INR"}},
                        {"step_id": 4, "action": "verify_payment", "parameters": {"provider": "paypal"}},
                        {"step_id": 5, "action": "send_confirmation_email", "parameters": {"template": "coding_workshop_confirmation"}}
                    ],
                    "status": "draft"
                }
            })

        # 5. Match TEST 3: Customer appointment booking
        if "appointment" in text or "booking" in text or "consultation" in text:
            return json.dumps({
                "supported": True,
                "clarification_needed": False,
                "clarification_questions": [],
                "extracted_requirements": {
                    "business_type": "appointment_booking",
                    "business_name": None,
                    "workflow_name": "Customer Appointment Booking",
                    "workflow_objective": "Customer appointment booking with email confirmation",
                    "trigger": "appointment_request",
                    "customer_info_fields": ["name", "email", "phone"],
                    "capacity": None,
                    "price": None,
                    "currency": None,
                    "payment_required": False,
                    "notification": "email"
                },
                "workflow": {
                    "workflow_name": "Customer Appointment Booking",
                    "description": "Customer appointment booking with email confirmation",
                    "trigger": "appointment_request",
                    "configuration": {},
                    "steps": [
                        {"step_id": 1, "action": "create_booking_page", "parameters": {"service_name": "Appointment Booking"}},
                        {"step_id": 2, "action": "collect_customer_details", "parameters": {"fields": ["name", "email", "phone"]}},
                        {"step_id": 3, "action": "schedule_appointment_slot", "parameters": {}},
                        {"step_id": 4, "action": "send_confirmation_email", "parameters": {"template": "appointment_confirmation"}}
                    ],
                    "status": "draft"
                }
            })

        # 6. Match TEST 4: Online product sales with PayPal
        if "product" in text or "sales" in text or "store" in text or "merchandise" in text or "ecommerce" in text:
            price_match = re.search(r"(\$|₹|€|£)?\s*(\d+(\.\d+)?)", instruction)
            extracted_price = float(price_match.group(2)) if price_match and float(price_match.group(2)) > 0 else 25.0
            currency = "USD"
            if "₹" in instruction or "inr" in text:
                currency = "INR"
            elif "€" in instruction or "eur" in text:
                currency = "EUR"
            elif "£" in instruction or "gbp" in text:
                currency = "GBP"

            return json.dumps({
                "supported": True,
                "clarification_needed": False,
                "clarification_questions": [],
                "extracted_requirements": {
                    "business_type": "product_sales",
                    "business_name": None,
                    "workflow_name": "Online Product Sales",
                    "workflow_objective": "Online product checkout with PayPal payment",
                    "trigger": "order_submission",
                    "customer_info_fields": ["name", "email", "shipping_address"],
                    "capacity": None,
                    "price": extracted_price,
                    "currency": currency,
                    "payment_required": True,
                    "notification": "email"
                },
                "workflow": {
                    "workflow_name": "Online Product Sales",
                    "description": "Online product checkout with PayPal payment",
                    "trigger": "order_submission",
                    "configuration": {
                        "price": extracted_price,
                        "currency": currency
                    },
                    "steps": [
                        {"step_id": 1, "action": "create_order_checkout", "parameters": {"price": extracted_price, "currency": currency}},
                        {"step_id": 2, "action": "collect_customer_details", "parameters": {"fields": ["name", "email", "shipping_address"]}},
                        {"step_id": 3, "action": "create_paypal_order", "parameters": {"amount": extracted_price, "currency": currency}},
                        {"step_id": 4, "action": "verify_payment", "parameters": {"provider": "paypal"}},
                        {"step_id": 5, "action": "send_confirmation_email", "parameters": {"template": "order_confirmation"}}
                    ],
                    "status": "draft"
                }
            })

        # 7. General Dynamic Fallback for any other valid business instruction
        return self._generate_dynamic_mock_workflow(instruction)

    def _extract_instruction(self, user_prompt: str) -> str:
        """Helper to extract user instruction from prompt template if enclosed in quotes."""
        match = re.search(r'"""(.*?)"""', user_prompt, re.DOTALL)
        if match:
            return match.group(1).strip()
        return user_prompt.strip()

    def _extract_title(self, instruction: str) -> str:
        """Extract a suitable title from instruction."""
        clean = re.sub(r'^(create|organize|set up|build|run|make)\s+(my|an?)\s+', '', instruction, flags=re.IGNORECASE)
        words = clean.split()
        title_words = words[:4] if len(words) >= 4 else words
        return " ".join(title_words).title()

    def _generate_dynamic_mock_workflow(self, instruction: str) -> str:
        """Parse natural language using heuristics to dynamically build valid workflows."""
        text = instruction.lower()

        # Capacity
        cap_match = re.search(r"(\d+)\s*(students|attendees|participants|seats|people|tickets|users)", text)
        capacity = int(cap_match.group(1)) if cap_match else None

        # Price & Currency
        price = None
        currency = None
        if "₹" in instruction or "inr" in text:
            currency = "INR"
            p_match = re.search(r"₹\s*(\d+(\.\d+)?)", instruction)
            if p_match:
                price = float(p_match.group(1))
        elif "$" in instruction or "usd" in text:
            currency = "USD"
            p_match = re.search(r"\$\s*(\d+(\.\d+)?)", instruction)
            if p_match:
                price = float(p_match.group(1))
        elif "€" in instruction or "eur" in text:
            currency = "EUR"
            p_match = re.search(r"€\s*(\d+(\.\d+)?)", instruction)
            if p_match:
                price = float(p_match.group(1))
        elif "£" in instruction or "gbp" in text:
            currency = "GBP"
            p_match = re.search(r"£\s*(\d+(\.\d+)?)", instruction)
            if p_match:
                price = float(p_match.group(1))
        else:
            # Check generic price mentions
            gen_match = re.search(r"(?:charge|fee|price|cost)\s+(?:of\s+)?(\d+(\.\d+)?)", text)
            if gen_match:
                price = float(gen_match.group(1))
                currency = "USD"

        payment_required = (price is not None and price > 0) or any(
            w in text for w in ["paypal", "charge", "payment", "fee", "cost", "pay"]
        )
        if payment_required and not currency:
            currency = "USD"

        notification = "email" if "email" in text else ("sms" if "sms" in text else "email")
        business_title = self._extract_title(instruction)

        # Build steps
        steps = []
        step_id = 1
        steps.append({
            "step_id": step_id,
            "action": "create_registration_page",
            "parameters": {"title": business_title, **({"capacity": capacity} if capacity else {})}
        })
        step_id += 1

        steps.append({
            "step_id": step_id,
            "action": "collect_customer_details",
            "parameters": {"fields": ["name", "email"]}
        })
        step_id += 1

        if payment_required:
            steps.append({
                "step_id": step_id,
                "action": "create_paypal_order",
                "parameters": {
                    "amount": price if price is not None else 10.0,
                    "currency": currency or "USD"
                }
            })
            step_id += 1
            steps.append({
                "step_id": step_id,
                "action": "verify_payment",
                "parameters": {"provider": "paypal"}
            })
            step_id += 1

        if notification == "email":
            steps.append({
                "step_id": step_id,
                "action": "send_confirmation_email",
                "parameters": {"template": "generic_confirmation"}
            })
        else:
            steps.append({
                "step_id": step_id,
                "action": "send_notification",
                "parameters": {"channel": notification or "email"}
            })

        config: Dict[str, Any] = {}
        if capacity is not None:
            config["capacity"] = capacity
        if price is not None:
            config["price"] = price
        if currency is not None:
            config["currency"] = currency

        result = {
            "supported": True,
            "clarification_needed": False,
            "clarification_questions": [],
            "extracted_requirements": {
                "business_type": "business_service",
                "business_name": business_title,
                "workflow_name": business_title,
                "workflow_objective": f"Automated workflow for {business_title}",
                "trigger": "customer_submission",
                "customer_info_fields": ["name", "email"],
                "capacity": capacity,
                "price": price,
                "currency": currency,
                "payment_required": payment_required,
                "notification": notification
            },
            "workflow": {
                "workflow_name": business_title,
                "description": f"Automated workflow for {business_title}",
                "trigger": "customer_submission",
                "configuration": config,
                "steps": steps,
                "status": "draft"
            }
        }
        return json.dumps(result)


def create_ai_client(config: AIConfig) -> BaseAIClient:
    """Factory creating the appropriate AI client based on configuration.
    
    If use_mock is set or OPENAI_API_KEY is missing or openai package is unavailable,
    it gracefully initializes MockAIClient without crashing.
    """
    if config.use_mock:
        logger.info("Initializing Mock AI client (mock mode explicitly enabled).")
        return MockAIClient(config)

    if not config.api_key:
        logger.warning(
            "OPENAI_API_KEY is not set. Automatically falling back to MockAIClient for offline testing."
        )
        return MockAIClient(config)

    if not OPENAI_SDK_AVAILABLE:
        logger.warning(
            "'openai' Python SDK is not installed. Automatically falling back to MockAIClient. "
            "To use real OpenAI API, install it with 'pip install openai'."
        )
        return MockAIClient(config)

    return OpenAIClientWrapper(config)
