"""Data models and schemas for FlowForge AI Engine.

Defines the structured schema for extracted business requirements,
individual workflow steps, the generated workflow contract, and validation outcomes.
Implemented with standard Python dataclasses for zero mandatory dependencies.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json


@dataclass
class BusinessRequirements:
    """Extracted business requirements from natural language instructions.
    
    Any missing information is represented as None (null in JSON).
    Never invent missing details.
    """
    business_type: Optional[str] = None
    business_name: Optional[str] = None
    workflow_name: Optional[str] = None
    workflow_objective: Optional[str] = None
    trigger: Optional[str] = None
    customer_info_fields: List[str] = field(default_factory=lambda: ["name", "email"])
    capacity: Optional[int] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    payment_required: bool = False
    notification: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert requirements to standard dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BusinessRequirements":
        """Instantiate BusinessRequirements from a dictionary, safely handling unexpected keys."""
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class WorkflowStep:
    """Individual action step in the workflow."""
    step_id: int
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowStep":
        return cls(
            step_id=int(data.get("step_id", 0)),
            action=str(data.get("action", "")),
            parameters=dict(data.get("parameters", {})),
        )


@dataclass
class WorkflowConfiguration:
    """Configuration parameters for the overall workflow."""
    capacity: Optional[int] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.capacity is not None:
            d["capacity"] = self.capacity
        if self.price is not None:
            d["price"] = self.price
        if self.currency is not None:
            d["currency"] = self.currency
        d.update(self.extra_config)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowConfiguration":
        capacity = data.get("capacity")
        price = data.get("price")
        currency = data.get("currency")
        extras = {k: v for k, v in data.items() if k not in ("capacity", "price", "currency")}
        return cls(
            capacity=int(capacity) if capacity is not None else None,
            price=float(price) if price is not None else None,
            currency=str(currency) if currency is not None else None,
            extra_config=extras,
        )


@dataclass
class Workflow:
    """Complete generated business workflow.
    
    This matches the official FlowForge AI contract for the Execution Engine.
    """
    workflow_name: str
    description: str
    trigger: str
    configuration: Dict[str, Any]
    steps: List[WorkflowStep]
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "description": self.description,
            "trigger": self.trigger,
            "configuration": self.configuration,
            "steps": [step.to_dict() for step in self.steps],
            "status": self.status,
            **({"metadata": self.metadata} if self.metadata else {}),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize workflow to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        steps_raw = data.get("steps", [])
        steps = [WorkflowStep.from_dict(s) for s in steps_raw]
        return cls(
            workflow_name=str(data.get("workflow_name", "")),
            description=str(data.get("description", "")),
            trigger=str(data.get("trigger", "")),
            configuration=dict(data.get("configuration", {})),
            steps=steps,
            status=str(data.get("status", "draft")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ValidationResult:
    """Result of workflow validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowGenerationResult:
    """Comprehensive result returned by the WorkflowGenerator."""
    success: bool
    extracted_requirements: Optional[Dict[str, Any]] = None
    workflow: Optional[Dict[str, Any]] = None
    validation: Optional[ValidationResult] = None
    clarification_needed: bool = False
    clarification_questions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "extracted_requirements": self.extracted_requirements,
            "workflow": self.workflow,
            "validation": self.validation.to_dict() if self.validation else None,
            "clarification_needed": self.clarification_needed,
            "clarification_questions": self.clarification_questions,
            "errors": self.errors,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

