"""API endpoints for creating, querying, updating, and managing business workflows."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.routes.auth import get_current_user, get_optional_current_user
from app.schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowStatusUpdateRequest,
    GenerateWorkflowRequest,
)
from app.services.workflow_service import WorkflowService, workflow_to_frontend_dict
from app.services.ai_service import AIService
from app.core.exceptions import EntityNotFoundException

logger = logging.getLogger("flowforge.routes.workflows")

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get(
    "",
    summary="List All Workflows",
    response_description="Array of workflows formatted for dashboard compatibility",
)
def list_workflows(
    status: Optional[str] = Query(None, description="Filter by status (e.g. active, draft)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[Dict[str, Any]]:
    """Retrieve all workflows, optionally filtered by status."""
    status_filter = status if isinstance(status, str) else None
    owner_id = current_user.id if isinstance(current_user, User) else None
    workflows = WorkflowService.list_workflows(db, owner_id=owner_id, status=status_filter)
    return [workflow_to_frontend_dict(wf, db=db) for wf in workflows]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create New Workflow",
    response_description="Newly created workflow object",
)
def create_workflow(
    payload: WorkflowCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Manually create and persist a new workflow."""
    owner_id = current_user.id if isinstance(current_user, User) else None
    workflow = WorkflowService.create_workflow(db, payload, owner_id=owner_id)
    return workflow_to_frontend_dict(workflow, db=db)


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate Workflow Using AI Engine",
    response_description="AI-generated workflow conforming to frontend contract",
)
def generate_workflow(
    payload: GenerateWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Accept natural language prompt, execute AI Engine generation, and persist workflow."""
    owner_id = current_user.id if isinstance(current_user, User) else None
    workflow = AIService.generate_and_save_workflow(db, payload.prompt, owner_id=owner_id)
    return workflow_to_frontend_dict(workflow, db=db)


@router.get(
    "/{workflow_id}",
    summary="Retrieve Workflow By ID",
    response_description="Workflow object including operational steps and configuration",
)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve a single workflow by its primary ID."""
    workflow = WorkflowService.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise EntityNotFoundException("Workflow", workflow_id)
    return workflow_to_frontend_dict(workflow, db=db)


@router.put(
    "/{workflow_id}",
    summary="Update Workflow Configuration",
    response_description="Updated workflow object",
)
def update_workflow(
    workflow_id: str,
    payload: WorkflowUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Update title, description, pricing, capacity, or steps for an existing workflow."""
    user_id = current_user.id if isinstance(current_user, User) else None
    workflow = WorkflowService.update_workflow(db, workflow_id, payload, current_user_id=user_id)
    return workflow_to_frontend_dict(workflow, db=db)


@router.delete(
    "/{workflow_id}",
    summary="Delete Workflow",
    response_description="Confirmation of successful deletion",
)
def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Delete a workflow and its associated registrations."""
    user_id = current_user.id if isinstance(current_user, User) else None
    WorkflowService.delete_workflow(db, workflow_id, current_user_id=user_id)
    return {"success": True, "message": f"Workflow '{workflow_id}' deleted successfully."}


@router.patch(
    "/{workflow_id}/status",
    summary="Update Workflow Status",
    response_description="Updated workflow with new status",
)
def set_workflow_status(
    workflow_id: str,
    payload: WorkflowStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """Activate, pause, or complete a workflow."""
    user_id = current_user.id if isinstance(current_user, User) else None
    workflow = WorkflowService.set_status(db, workflow_id, payload.status, current_user_id=user_id)
    return workflow_to_frontend_dict(workflow, db=db)
