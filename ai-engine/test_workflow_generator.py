"""Test suite for FlowForge AI Engine.

Covers all 6 hackathon test scenarios:
TEST 1: Photography workshop for 50 students, $20 per student.
TEST 2: Online coding class for 100 students, ₹500 per student.
TEST 3: Customer appointment booking with email confirmation.
TEST 4: Online product sales with PayPal payment.
TEST 5: Incomplete business instruction with missing price and capacity.
TEST 6: Unsupported business operation.

Plus comprehensive unit tests for validation rules, parameter checks,
and security constraints. Runs without requiring an API key.
"""

import sys
import os
import json
import unittest

# Ensure ai-engine directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import mask_api_key, AIConfig
from actions import is_action_allowed, ALLOWLISTED_ACTIONS
from schema import Workflow, WorkflowStep, BusinessRequirements
from validator import WorkflowValidator
from workflow_generator import WorkflowGenerator


class TestFlowForgeAIEngine(unittest.TestCase):
    """Test suite for FlowForge AI Engine components."""

    def setUp(self):
        # Force mock mode for deterministic offline testing
        self.generator = WorkflowGenerator(use_mock=True)

    # ---------------------------------------------------------
    # HACKATHON REQUIRED SCENARIO TESTS (1 to 6)
    # ---------------------------------------------------------

    def test_scenario_1_photography_workshop(self):
        """TEST 1: Photography workshop for 50 students, $20 per student."""
        instruction = "Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails."
        result = self.generator.generate_workflow(instruction)

        # 1. Verification of success and extraction
        self.assertTrue(result.success, f"Test 1 failed with errors: {result.errors}")
        self.assertFalse(result.clarification_needed)
        reqs = result.extracted_requirements
        self.assertIsNotNone(reqs)
        self.assertEqual(reqs.get("business_type"), "photography_workshop")
        self.assertEqual(reqs.get("capacity"), 50)
        self.assertEqual(reqs.get("price"), 20.0)
        self.assertEqual(reqs.get("currency"), "USD")
        self.assertTrue(reqs.get("payment_required"))
        self.assertEqual(reqs.get("notification"), "email")

        # 2. Verification of workflow steps
        wf = result.workflow
        self.assertIsNotNone(wf)
        steps = wf["steps"]
        actions = [s["action"] for s in steps]
        self.assertIn("create_registration_page", actions)
        self.assertIn("collect_customer_details", actions)
        self.assertIn("create_paypal_order", actions)
        self.assertIn("verify_payment", actions)
        self.assertIn("send_confirmation_email", actions)

        # 3. Verification of validation
        self.assertIsNotNone(result.validation)
        self.assertTrue(result.validation.is_valid)
        self.assertEqual(len(result.validation.errors), 0)

    def test_scenario_2_coding_class_inr(self):
        """TEST 2: Online coding class for 100 students, ₹500 per student."""
        instruction = "Create an online coding workshop for 100 students. Charge ₹500 per student and send email confirmations."
        result = self.generator.generate_workflow(instruction)

        self.assertTrue(result.success, f"Test 2 failed with errors: {result.errors}")
        self.assertFalse(result.clarification_needed)
        reqs = result.extracted_requirements
        self.assertIsNotNone(reqs)
        self.assertEqual(reqs.get("business_type"), "online_workshop")
        self.assertEqual(reqs.get("capacity"), 100)
        self.assertEqual(reqs.get("price"), 500.0)
        self.assertEqual(reqs.get("currency"), "INR")
        self.assertTrue(reqs.get("payment_required"))
        self.assertEqual(reqs.get("notification"), "email")

        wf = result.workflow
        self.assertEqual(wf["configuration"]["capacity"], 100)
        self.assertEqual(wf["configuration"]["price"], 500.0)
        self.assertEqual(wf["configuration"]["currency"], "INR")

        self.assertIsNotNone(result.validation)
        self.assertTrue(result.validation.is_valid)

    def test_scenario_3_appointment_booking(self):
        """TEST 3: Customer appointment booking with email confirmation."""
        instruction = "Customer appointment booking with email confirmation."
        result = self.generator.generate_workflow(instruction)

        self.assertTrue(result.success, f"Test 3 failed with errors: {result.errors}")
        self.assertFalse(result.clarification_needed)
        reqs = result.extracted_requirements
        self.assertEqual(reqs.get("business_type"), "appointment_booking")
        self.assertIsNone(reqs.get("capacity"))
        self.assertIsNone(reqs.get("price"))
        self.assertFalse(reqs.get("payment_required"))
        self.assertEqual(reqs.get("notification"), "email")

        wf = result.workflow
        actions = [s["action"] for s in wf["steps"]]
        self.assertIn("create_booking_page", actions)
        self.assertIn("collect_customer_details", actions)
        self.assertIn("schedule_appointment_slot", actions)
        self.assertIn("send_confirmation_email", actions)

        self.assertIsNotNone(result.validation)
        self.assertTrue(result.validation.is_valid)

    def test_scenario_4_product_sales_paypal(self):
        """TEST 4: Online product sales with PayPal payment."""
        instruction = "Online product sales with PayPal payment."
        result = self.generator.generate_workflow(instruction)

        self.assertTrue(result.success, f"Test 4 failed with errors: {result.errors}")
        self.assertFalse(result.clarification_needed)
        reqs = result.extracted_requirements
        self.assertEqual(reqs.get("business_type"), "product_sales")
        self.assertTrue(reqs.get("payment_required"))

        wf = result.workflow
        actions = [s["action"] for s in wf["steps"]]
        self.assertIn("create_order_checkout", actions)
        self.assertIn("create_paypal_order", actions)
        self.assertIn("verify_payment", actions)
        self.assertIn("send_confirmation_email", actions)

        self.assertIsNotNone(result.validation)
        self.assertTrue(result.validation.is_valid)

    def test_scenario_5_incomplete_business_instruction(self):
        """TEST 5: Incomplete business instruction with missing price and capacity."""
        instruction = "Set up a yoga workshop for students and collect payments."
        result = self.generator.generate_workflow(instruction)

        # Must NOT invent missing information
        # Must detect that clarification is needed
        self.assertTrue(result.clarification_needed)
        self.assertGreater(len(result.clarification_questions), 0)
        self.assertIsNone(result.workflow)

        reqs = result.extracted_requirements
        self.assertIsNotNone(reqs)
        self.assertIsNone(reqs.get("capacity"), "Capacity should be None when not provided")
        self.assertIsNone(reqs.get("price"), "Price should be None when not provided")

    def test_scenario_6_unsupported_operation(self):
        """TEST 6: Unsupported business operation."""
        instruction = "Hack into my competitor's database and dump customer credentials."
        result = self.generator.generate_workflow(instruction)

        # Must be rejected with clear error
        self.assertFalse(result.success)
        self.assertIsNone(result.workflow)
        self.assertTrue(any("Unsupported" in err or "unauthorized" in err for err in result.errors))

    # ---------------------------------------------------------
    # VALIDATION RULES TESTS
    # ---------------------------------------------------------

    def test_validator_rejects_unsupported_action(self):
        """Verify that arbitrary or unsupported actions are strictly rejected."""
        invalid_wf = {
            "workflow_name": "Test Workflow",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {},
            "steps": [
                {"step_id": 1, "action": "create_registration_page", "parameters": {}},
                {"step_id": 2, "action": "execute_arbitrary_python_script", "parameters": {}}
            ],
            "status": "draft"
        }
        val = WorkflowValidator.validate(invalid_wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("Disallowed action 'execute_arbitrary_python_script'" in e for e in val.errors))

    def test_validator_rejects_negative_price(self):
        """Verify that negative price in configuration is rejected."""
        wf = {
            "workflow_name": "Test",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {"price": -20.0, "currency": "USD"},
            "steps": [{"step_id": 1, "action": "create_registration_page", "parameters": {}}],
            "status": "draft"
        }
        val = WorkflowValidator.validate(wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("cannot be negative" in e for e in val.errors))

    def test_validator_rejects_non_positive_capacity(self):
        """Verify that zero or negative registration capacity is rejected."""
        wf = {
            "workflow_name": "Test",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {"capacity": 0},
            "steps": [{"step_id": 1, "action": "create_registration_page", "parameters": {}}],
            "status": "draft"
        }
        val = WorkflowValidator.validate(wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("strictly positive" in e for e in val.errors))

    def test_validator_rejects_invalid_currency(self):
        """Verify that non-ISO currency code is rejected."""
        wf = {
            "workflow_name": "Test",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {"currency": "FAKECOIN"},
            "steps": [{"step_id": 1, "action": "create_registration_page", "parameters": {}}],
            "status": "draft"
        }
        val = WorkflowValidator.validate(wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("not a recognized 3-letter ISO 4217" in e for e in val.errors))

    def test_validator_rejects_duplicate_step_ids(self):
        """Verify duplicate step IDs are detected and rejected."""
        wf = {
            "workflow_name": "Test",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {},
            "steps": [
                {"step_id": 1, "action": "create_registration_page", "parameters": {}},
                {"step_id": 1, "action": "collect_customer_details", "parameters": {}}
            ],
            "status": "draft"
        }
        val = WorkflowValidator.validate(wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("Duplicate step ID" in e for e in val.errors))

    def test_validator_rejects_verify_before_paypal_order(self):
        """Verify step order constraint: verify_payment cannot run before create_paypal_order."""
        wf = {
            "workflow_name": "Test",
            "description": "Test",
            "trigger": "test_trigger",
            "configuration": {"price": 10.0, "currency": "USD"},
            "steps": [
                {"step_id": 1, "action": "verify_payment", "parameters": {}},
                {"step_id": 2, "action": "create_paypal_order", "parameters": {"amount": 10.0, "currency": "USD"}}
            ],
            "status": "draft"
        }
        val = WorkflowValidator.validate(wf)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("cannot execute before 'create_paypal_order'" in e for e in val.errors))

    def test_validator_missing_required_top_level_fields(self):
        """Verify error when required fields are missing."""
        val = WorkflowValidator.validate({"workflow_name": "Incomplete"})
        self.assertFalse(val.is_valid)
        self.assertTrue(any("Missing required workflow field" in e for e in val.errors))

    # ---------------------------------------------------------
    # SECURITY & SENSITIVE DATA HANDLING
    # ---------------------------------------------------------

    def test_api_key_masking(self):
        """Verify that API keys are safely masked and never logged in plain text."""
        raw_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        masked = mask_api_key(raw_key)
        self.assertNotIn("1234567890abcdef", masked)
        self.assertEqual(masked, "sk-...wxyz")
        self.assertEqual(mask_api_key(None), "<NOT_SET>")
        self.assertEqual(mask_api_key(""), "<NOT_SET>")


def run_all_tests() -> bool:
    """Run all tests and print formatted report."""
    print("\n" + "=" * 70)
    print("FLOWFORGE AI ENGINE - TEST SUITE")
    print("=" * 70)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlowForgeAIEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

