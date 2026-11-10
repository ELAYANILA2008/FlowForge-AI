"""Workflow Generator for FlowForge AI.

Core orchestration engine responsible for:
1. Accepting natural language business instructions.
2. Analyzing intent and extracting business requirements.
3. Identifying allowlisted workflow actions.
4. Generating structured JSON workflows.
5. Validating workflows against strict business rules and schema.
6. Returning validated results or clarification questions.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any, Union

try:
    from .config import AIConfig, logger
    from .openai_client import (
        create_ai_client,
        BaseAIClient,
        FlowForgeAIError,
        FlowForgeAuthenticationError,
        FlowForgeConnectionError,
        FlowForgeRateLimitError,
        FlowForgeTimeoutError,
        FlowForgeInvalidResponseError,
    )
    from .schema import (
        BusinessRequirements,
        Workflow,
        ValidationResult,
        WorkflowGenerationResult,
    )
    from .validator import WorkflowValidator
except (ImportError, ValueError):
    from config import AIConfig, logger
    from openai_client import (
        create_ai_client,
        BaseAIClient,
        FlowForgeAIError,
        FlowForgeAuthenticationError,
        FlowForgeConnectionError,
        FlowForgeRateLimitError,
        FlowForgeTimeoutError,
        FlowForgeInvalidResponseError,
    )
    from schema import (
        BusinessRequirements,
        Workflow,
        ValidationResult,
        WorkflowGenerationResult,
    )
    from validator import WorkflowValidator


class WorkflowGenerator:
    """Orchestrates natural language understanding, OpenAI LLM completion,
    and workflow generation & validation for FlowForge AI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_mock: Optional[bool] = None,
        timeout: Optional[float] = None,
    ):
        """Initialize the WorkflowGenerator.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to OPENAI_MODEL or 'gpt-4o-mini')
            use_mock: Explicitly enable or disable mock mode
            timeout: Timeout in seconds for LLM calls (defaults to 30.0)
        """
        self.config = AIConfig(
            api_key=api_key,
            model=model,
            timeout=timeout,
            use_mock=use_mock,
        )
        self.config.log_status()
        self.ai_client: BaseAIClient = create_ai_client(self.config)

        # Load prompts
        self.prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.system_prompt = self._load_prompt("system_prompt.txt")
        self.user_prompt_template = self._load_prompt("user_prompt_template.txt")

    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from prompts directory."""
        filepath = os.path.join(self.prompts_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        logger.warning("Prompt file not found at %s. Using default internal prompt.", filepath)
        return ""

    def extract_requirements(self, user_instruction: str) -> Dict[str, Any]:
        """Extract business requirements from natural language instruction.
        
        Returns dictionary conforming to the BusinessRequirements schema.
        Never invents missing information.
        """
        result = self.generate_workflow(user_instruction)
        return result.extracted_requirements or {}

    def generate_workflow(self, user_instruction: str) -> WorkflowGenerationResult:
        """Main method: Accept instruction, extract requirements, generate JSON,
        validate workflow, and return comprehensive WorkflowGenerationResult.
        
        Args:
            user_instruction: Natural language prompt from small business owner.
            
        Returns:
            WorkflowGenerationResult containing workflow, extraction, validation, and status.
        """
        if not user_instruction or not user_instruction.strip():
            return WorkflowGenerationResult(
                success=False,
                errors=["User instruction cannot be empty."],
            )

        trimmed_instruction = user_instruction.strip()
        logger.info("Processing business instruction: '%s'", trimmed_instruction)

        # Build prompts
        system_prompt = self.system_prompt
        if not system_prompt:
            system_prompt = (
                "You are FlowForge AI, a business workflow generation assistant. "
                "Generate valid JSON workflows from natural language instructions. "
                "Do not execute code. Only use allowlisted actions."
            )

        if self.user_prompt_template:
            user_prompt = self.user_prompt_template.replace("{user_instruction}", trimmed_instruction)
        else:
            user_prompt = f"User instruction: {trimmed_instruction}"

        # Call AI Client (OpenAI SDK or Mock)
        try:
            raw_response = self.ai_client.complete(system_prompt, user_prompt)
        except FlowForgeAuthenticationError as auth_err:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Authentication Error: {str(auth_err)}"],
            )
        except FlowForgeRateLimitError as rate_err:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Rate Limit Error: {str(rate_err)}"],
            )
        except FlowForgeTimeoutError as timeout_err:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Timeout Error: {str(timeout_err)}"],
            )
        except FlowForgeConnectionError as conn_err:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Connection Error: {str(conn_err)}"],
            )
        except FlowForgeAIError as ai_err:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"AI Error: {str(ai_err)}"],
            )
        except Exception as exc:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Unexpected processing error: {str(exc)}"],
            )

        # Parse LLM JSON response
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as json_exc:
            return WorkflowGenerationResult(
                success=False,
                errors=[f"Invalid JSON returned by AI model: {str(json_exc)}"],
            )

        if not isinstance(parsed, dict):
            return WorkflowGenerationResult(
                success=False,
                errors=["Model response root must be a JSON object."],
            )

        # Check if operation was deemed unsupported
        if parsed.get("supported") is False:
            rejection_reason = parsed.get(
                "rejection_reason",
                "Unsupported business operation: The requested operation is outside the scope of business workflow automation."
            )
            return WorkflowGenerationResult(
                success=False,
                clarification_needed=False,
                errors=[rejection_reason],
            )

        # Extract requirements
        extracted = parsed.get("extracted_requirements")
        clarification_needed = bool(parsed.get("clarification_needed", False))
        clarification_questions = parsed.get("clarification_questions", [])

        # If clarification is needed, return early with questions
        if clarification_needed:
            return WorkflowGenerationResult(
                success=True,
                extracted_requirements=extracted,
                workflow=None,
                clarification_needed=True,
                clarification_questions=clarification_questions,
            )

        workflow_data = parsed.get("workflow")
        if not workflow_data:
            return WorkflowGenerationResult(
                success=False,
                extracted_requirements=extracted,
                errors=["AI model did not return a workflow object."],
            )

        # Validate generated workflow
        validation = self.validate_workflow(workflow_data)

        if not validation.is_valid:
            logger.warning("Generated workflow failed validation: %s", validation.errors)
            return WorkflowGenerationResult(
                success=False,
                extracted_requirements=extracted,
                workflow=workflow_data,
                validation=validation,
                errors=validation.errors,
            )

        logger.info("Successfully generated and validated workflow: '%s'", workflow_data.get("workflow_name"))
        return WorkflowGenerationResult(
            success=True,
            extracted_requirements=extracted,
            workflow=workflow_data,
            validation=validation,
            clarification_needed=False,
            clarification_questions=[],
            errors=[],
        )

    def validate_workflow(self, workflow_data: Union[str, Dict[str, Any]]) -> ValidationResult:
        """Validate a workflow against all business rules and schemas."""
        return WorkflowValidator.validate(workflow_data)


def main():
    """Command-line interface for the FlowForge AI Workflow Generator."""
    parser = argparse.ArgumentParser(
        description="FlowForge AI - Automated Business Workflow Generator"
    )
    parser.add_argument(
        "instruction",
        nargs="?",
        type=str,
        help="Natural language business instruction to process",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock AI client mode (no API key required)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-test suite across hackathon scenarios",
    )

    args = parser.parse_args()

    if args.test:
        from .test_workflow_generator import run_all_tests
        success = run_all_tests()
        sys.exit(0 if success else 1)

    if not args.instruction:
        print("\nFlowForge AI Workflow Generator")
        print("Usage: python workflow_generator.py \"Your business instruction here\"")
        print("Example: python workflow_generator.py \"Organize my photography workshop for 50 students. Charge $20 per student and send confirmation emails.\"\n")
        print("Flags:")
        print("  --mock     Run in mock mode (offline, no API key needed)")
        print("  --test     Run verification test suite")
        return

    generator = WorkflowGenerator(use_mock=args.mock, model=args.model)
    result = generator.generate_workflow(args.instruction)

    print("\n" + "=" * 60)
    print("FLOWFORGE AI WORKFLOW GENERATION RESULT")
    print("=" * 60)
    print(result.to_json(indent=2))


if __name__ == "__main__":
    main()
