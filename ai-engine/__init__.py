"""FlowForge AI Engine package.

AI-powered natural language understanding, business requirement extraction,
and automated workflow generation for PayPal-integrated business operations.
"""

try:
    from .workflow_generator import WorkflowGenerator
    from .schema import (
        Workflow,
        WorkflowStep,
        WorkflowConfiguration,
        BusinessRequirements,
        ValidationResult,
        WorkflowGenerationResult,
    )
    from .validator import WorkflowValidator
    from .actions import ALLOWLISTED_ACTIONS, is_action_allowed
except (ImportError, ValueError):
    from workflow_generator import WorkflowGenerator
    from schema import (
        Workflow,
        WorkflowStep,
        WorkflowConfiguration,
        BusinessRequirements,
        ValidationResult,
        WorkflowGenerationResult,
    )
    from validator import WorkflowValidator
    from actions import ALLOWLISTED_ACTIONS, is_action_allowed

__all__ = [
    "WorkflowGenerator",
    "Workflow",
    "WorkflowStep",
    "WorkflowConfiguration",
    "BusinessRequirements",
    "ValidationResult",
    "WorkflowGenerationResult",
    "WorkflowValidator",
    "ALLOWLISTED_ACTIONS",
    "is_action_allowed",
]
