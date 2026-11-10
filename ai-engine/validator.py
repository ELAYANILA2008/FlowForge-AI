"""Workflow Validator for FlowForge AI.

Validates generated workflows against JSON structure, required fields,
allowlisted actions, step sequencing, parameter integrity, business constraints
(positive capacity, non-negative price, ISO currencies), and missing requirements.
"""

import json
import re
from typing import Dict, Any, List, Union
try:
    from .actions import is_action_allowed, get_action_metadata, get_allowed_actions_list
    from .schema import ValidationResult
except (ImportError, ValueError):
    from actions import is_action_allowed, get_action_metadata, get_allowed_actions_list
    from schema import ValidationResult

# Common ISO 4217 3-letter currency codes (supported by PayPal & global commerce)
VALID_CURRENCY_CODES = {
    "USD", "EUR", "GBP", "INR", "CAD", "AUD", "JPY", "SGD", "CHF", "HKD",
    "NZD", "SEK", "NOK", "DKK", "PLN", "ILS", "MXN", "BRL", "MYR", "PHP",
    "TWD", "THB", "CZK", "HUF"
}

VALID_STATUSES = {"draft", "active", "published", "needs_clarification", "archived"}


class WorkflowValidator:
    """Strict validator for FlowForge AI business workflows."""

    @classmethod
    def validate(cls, workflow_input: Union[str, Dict[str, Any]]) -> ValidationResult:
        """Validate a workflow JSON string or dictionary.
        
        Returns a ValidationResult object with is_valid boolean and detailed errors.
        """
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        # 1. Structure validation
        data: Dict[str, Any]
        if isinstance(workflow_input, str):
            try:
                data = json.loads(workflow_input)
            except json.JSONDecodeError as exc:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Invalid JSON format: {str(exc)}"],
                    warnings=[],
                    details={"json_error": str(exc)},
                )
        elif isinstance(workflow_input, dict):
            data = workflow_input
        else:
            return ValidationResult(
                is_valid=False,
                errors=[f"Workflow data must be a dict or JSON string, got {type(workflow_input).__name__}"],
                warnings=[],
            )

        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                errors=["Workflow root element must be a JSON object (dictionary)"],
                warnings=[],
            )

        # 2. Required top-level fields
        required_fields = ["workflow_name", "description", "trigger", "configuration", "steps", "status"]
        for field_name in required_fields:
            if field_name not in data:
                errors.append(f"Missing required workflow field: '{field_name}'")
            elif data[field_name] is None:
                errors.append(f"Field '{field_name}' cannot be null")

        # Early return if required fields are missing
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Validate types of top-level fields
        if not isinstance(data["workflow_name"], str) or not data["workflow_name"].strip():
            errors.append("Field 'workflow_name' must be a non-empty string")

        if not isinstance(data["description"], str) or not data["description"].strip():
            errors.append("Field 'description' must be a non-empty string")

        if not isinstance(data["trigger"], str) or not data["trigger"].strip():
            errors.append("Field 'trigger' must be a non-empty string")

        if not isinstance(data["configuration"], dict):
            errors.append("Field 'configuration' must be a JSON object (dictionary)")

        if not isinstance(data["steps"], list):
            errors.append("Field 'steps' must be a list of workflow steps")

        if data.get("status") not in VALID_STATUSES:
            errors.append(
                f"Field 'status' has invalid value '{data.get('status')}'. Must be one of: {sorted(list(VALID_STATUSES))}"
            )

        # If top-level types failed, return now
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 3. Validate Configuration constraints
        config = data["configuration"]
        cls._validate_configuration(config, errors, warnings)

        # 4. Validate Steps
        steps = data["steps"]
        if len(steps) == 0:
            errors.append("Workflow 'steps' list cannot be empty. At least one action step is required.")
        else:
            cls._validate_steps(steps, config, errors, warnings)

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            details=details,
        )

    @classmethod
    def _validate_configuration(
        cls, config: Dict[str, Any], errors: List[str], warnings: List[str]
    ) -> None:
        """Validate capacity, price, currency, and business requirements in configuration."""
        # Validate capacity
        if "capacity" in config and config["capacity"] is not None:
            capacity = config["capacity"]
            if isinstance(capacity, bool) or not isinstance(capacity, int):
                errors.append(
                    f"Configuration 'capacity' must be an integer, got {type(capacity).__name__} ({capacity})"
                )
            elif capacity <= 0:
                errors.append(f"Configuration 'capacity' must be a strictly positive integer (> 0), got: {capacity}")

        # Validate price
        if "price" in config and config["price"] is not None:
            price = config["price"]
            if isinstance(price, bool) or not isinstance(price, (int, float)):
                errors.append(f"Configuration 'price' must be a number, got {type(price).__name__} ({price})")
            elif price < 0:
                errors.append(f"Configuration 'price' cannot be negative, got: {price}")

        # Validate currency
        if "currency" in config and config["currency"] is not None:
            currency = config["currency"]
            if not isinstance(currency, str):
                errors.append(f"Configuration 'currency' must be a string, got {type(currency).__name__}")
            else:
                currency_upper = currency.strip().upper()
                if currency_upper not in VALID_CURRENCY_CODES:
                    errors.append(
                        f"Configuration 'currency' '{currency}' is not a recognized 3-letter ISO 4217 currency code"
                    )

    @classmethod
    def _validate_steps(
        cls, steps: List[Any], config: Dict[str, Any], errors: List[str], warnings: List[str]
    ) -> None:
        """Validate steps ordering, step IDs, allowlisted actions, and parameters."""
        seen_ids = set()
        actions_order: List[str] = []
        has_paypal_order = False
        has_payment_verification = False
        paypal_order_step_id = -1
        verify_step_id = -1

        for idx, step in enumerate(steps):
            step_pos = idx + 1
            if not isinstance(step, dict):
                errors.append(f"Step at index {idx} must be a dictionary, got {type(step).__name__}")
                continue

            # Validate step_id
            if "step_id" not in step:
                errors.append(f"Step at index {idx} is missing 'step_id'")
                step_id = step_pos
            else:
                step_id = step["step_id"]
                if isinstance(step_id, bool) or not isinstance(step_id, int):
                    errors.append(f"Step at index {idx} 'step_id' must be an integer, got: {step_id}")
                else:
                    if step_id in seen_ids:
                        errors.append(f"Duplicate step ID detected: {step_id} (at index {idx})")
                    seen_ids.add(step_id)

                    # Step IDs should ideally be 1, 2, 3...
                    if step_id != step_pos:
                        warnings.append(
                            f"Step at index {idx} has non-sequential step_id {step_id} (expected {step_pos})"
                        )

            # Validate action
            if "action" not in step:
                errors.append(f"Step {step_id} is missing 'action' field")
                continue

            action = step["action"]
            if not isinstance(action, str) or not action.strip():
                errors.append(f"Step {step_id} 'action' must be a non-empty string")
                continue

            action = action.strip()
            actions_order.append(action)

            # Check allowlist
            if not is_action_allowed(action):
                allowed = ", ".join(get_allowed_actions_list())
                errors.append(
                    f"Step {step_id}: Disallowed action '{action}'. Action must be one of approved allowlist: [{allowed}]"
                )
                continue

            # Validate parameters
            if "parameters" not in step:
                errors.append(f"Step {step_id} is missing 'parameters' field")
                parameters = {}
            elif not isinstance(step["parameters"], dict):
                errors.append(f"Step {step_id} 'parameters' must be a dictionary, got {type(step['parameters']).__name__}")
                parameters = {}
            else:
                parameters = step["parameters"]

            action_meta = get_action_metadata(action)
            if action_meta:
                # Check for required parameters
                for req_param in action_meta.get("required_parameters", []):
                    if req_param not in parameters or parameters[req_param] is None:
                        # For create_paypal_order, parameters might be filled from config
                        if action == "create_paypal_order":
                            if req_param == "amount" and config.get("price") is not None:
                                continue
                            if req_param == "currency" and config.get("currency") is not None:
                                continue
                        errors.append(f"Step {step_id} ('{action}') missing required parameter: '{req_param}'")

            # Specific checks for create_paypal_order
            if action == "create_paypal_order":
                has_paypal_order = True
                paypal_order_step_id = step_id

                # Validate amount if passed in parameters
                amount = parameters.get("amount", config.get("price"))
                if amount is None:
                    errors.append(
                        f"Step {step_id} ('create_paypal_order'): payment amount is missing (not in step parameters or workflow configuration)"
                    )
                elif isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
                    errors.append(
                        f"Step {step_id} ('create_paypal_order'): payment amount must be a positive number (> 0), got: {amount}"
                    )

                # Validate currency if passed in parameters
                currency = parameters.get("currency", config.get("currency"))
                if not currency:
                    errors.append(
                        f"Step {step_id} ('create_paypal_order'): currency is missing (not in step parameters or workflow configuration)"
                    )
                elif str(currency).strip().upper() not in VALID_CURRENCY_CODES:
                    errors.append(
                        f"Step {step_id} ('create_paypal_order'): invalid currency code '{currency}'"
                    )

            if action == "verify_payment":
                has_payment_verification = True
                verify_step_id = step_id

        # Logical sequencing checks:
        # 1. verify_payment cannot occur before create_paypal_order
        if has_payment_verification and not has_paypal_order:
            errors.append(
                "Invalid step ordering: 'verify_payment' action requires a preceding 'create_paypal_order' action"
            )
        elif has_payment_verification and has_paypal_order:
            if verify_step_id < paypal_order_step_id:
                errors.append(
                    f"Invalid step ordering: 'verify_payment' (step {verify_step_id}) cannot execute before 'create_paypal_order' (step {paypal_order_step_id})"
                )

        # 2. send_confirmation_email should appear after payment verification if payments are involved
        if has_payment_verification and "send_confirmation_email" in actions_order:
            email_idx = actions_order.index("send_confirmation_email")
            verify_idx = actions_order.index("verify_payment")
            if email_idx < verify_idx:
                warnings.append(
                    "Logical warning: 'send_confirmation_email' appears before 'verify_payment'. Confirmations are normally sent after payment is verified."
                )
