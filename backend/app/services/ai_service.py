"""AI Service Adapter for FlowForge AI Engine.

Integrates the completed ai-engine/ module without modifying any files inside ai-engine/.
Translates natural language prompts into validated, structured workflows and persists
them to PostgreSQL / SQLAlchemy.
"""

import os
import sys
import logging
from decimal import Decimal
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AIEngineException
from app.models.workflow import WorkflowModel
from app.utils.currency import normalize_currency, to_decimal_amount, format_currency_display
from app.services.workflow_service import generate_default_steps, workflow_to_frontend_dict

logger = logging.getLogger("flowforge.services.ai")

# Dynamically resolve and inject ai-engine path to sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
_AI_ENGINE_PATH = os.path.join(_PROJECT_ROOT, "ai-engine")

if os.path.isdir(_AI_ENGINE_PATH) and _AI_ENGINE_PATH not in sys.path:
    sys.path.insert(0, _AI_ENGINE_PATH)


class AIService:
    """Service adapter orchestrating the AI Engine and database persistence."""

    _generator = None

    @classmethod
    def get_generator(cls):
        """Lazy initialization of the WorkflowGenerator singleton."""
        if cls._generator is None:
            try:
                from workflow_generator import WorkflowGenerator
                cls._generator = WorkflowGenerator(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.OPENAI_MODEL,
                    use_mock=settings.AI_ENGINE_USE_MOCK,
                )
                logger.info("Initialized AI Engine adapter (mock_mode=%s, model=%s)",
                            settings.AI_ENGINE_USE_MOCK, settings.OPENAI_MODEL)
            except Exception as exc:
                logger.exception("Failed to initialize AI Engine WorkflowGenerator: %s", str(exc))
                raise AIEngineException(f"AI Engine initialization failed: {str(exc)}") from exc
        return cls._generator

    @classmethod
    def generate_and_save_workflow(
        cls,
        db: Session,
        prompt: str,
        owner_id: Optional[str] = None,
    ) -> WorkflowModel:
        """Process natural language instruction via AI Engine, validate, and persist workflow.
        
        Args:
            db: Active SQLAlchemy database session.
            prompt: User natural language instruction.
            owner_id: Optional user owner ID.
            
        Returns:
            Newly created and persisted WorkflowModel instance.
        """
        if not prompt or not prompt.strip():
            raise AIEngineException("Prompt instruction cannot be empty.")

        trimmed_prompt = prompt.strip()
        generator = cls.get_generator()

        # Execute AI Engine workflow generation
        try:
            result = generator.generate_workflow(trimmed_prompt)
        except Exception as exc:
            logger.exception("AI Engine execution failed on prompt '%s': %s", trimmed_prompt, str(exc))
            raise AIEngineException(f"Generation failed: {str(exc)}") from exc

        if not result.success:
            error_msg = "; ".join(result.errors) if result.errors else "Unknown AI Engine error."
            logger.warning("AI Engine rejected instruction '%s': %s", trimmed_prompt, error_msg)
            raise AIEngineException(error_msg, details={"errors": result.errors})

        raw_workflow = result.workflow or {}
        reqs = result.extracted_requirements or {}
        config = raw_workflow.get("configuration") or {}

        # Extract normalized workflow parameters
        title = raw_workflow.get("workflow_name") or reqs.get("workflow_name") or "Automated Business Operation"
        description = raw_workflow.get("description") or reqs.get("workflow_objective") or f"Generated operations for: {title}"

        # Extract capacity (default 50)
        raw_cap = config.get("capacity") or reqs.get("capacity") or 50
        try:
            capacity = max(1, int(raw_cap))
        except (ValueError, TypeError):
            capacity = 50

        # Extract price and currency
        raw_price = config.get("price") or reqs.get("price") or 20.00
        raw_curr = config.get("currency") or reqs.get("currency") or "USD"

        dec_price = to_decimal_amount(raw_price)
        validated_curr = normalize_currency(str(raw_curr))

        # Generate structured 5-step UI pipeline
        steps = generate_default_steps(capacity, dec_price, validated_curr)

        # Store full declarative metadata
        workflow_configuration = {
            "prompt": trimmed_prompt,
            "steps": steps,
            "raw_ai_output": raw_workflow,
            "extracted_requirements": reqs,
            "tags": ["AI Generated", "PayPal", "Auto-Operations"],
        }

        # Persist to database
        workflow = WorkflowModel(
            owner_id=owner_id,
            title=title,
            description=description,
            configuration=workflow_configuration,
            status="active",
            capacity=capacity,
            price=dec_price,
            currency=validated_curr,
        )

        try:
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
        except Exception as persist_exc:
            db.rollback()
            logger.exception(
                "Failed to persist AI-generated workflow to database: %s", str(persist_exc)
            )
            raise AIEngineException(
                f"Workflow generation succeeded but database persistence failed: {str(persist_exc)}",
                details={"prompt": trimmed_prompt, "title": title},
            ) from persist_exc

        logger.info(
            "AI Engine successfully generated and persisted workflow [%s] '%s' (capacity=%d, price=%s %s)",
            workflow.id, workflow.title, workflow.capacity, workflow.price, workflow.currency
        )
        return workflow
