"""Centralized exceptions and FastAPI error handlers.

Provides consistent error envelopes across all backend API responses:
{
    "success": false,
    "error": "ErrorType",
    "message": "Human-readable description",
    "details": {...}
}
"""

import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("flowforge.exceptions")


class FlowForgeException(Exception):
    """Base exception class for all domain-specific errors in FlowForge AI."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(FlowForgeException):
    """Raised when a requested resource does not exist."""

    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"entity": entity_name, "id": str(entity_id)},
        )


class DuplicateEntityException(FlowForgeException):
    """Raised when an entity with unique constraint already exists."""

    def __init__(self, entity_name: str, field_name: str, field_value: Any):
        super().__init__(
            message=f"{entity_name} with {field_name} '{field_value}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details={"entity": entity_name, "field": field_name, "value": str(field_value)},
        )


class CapacityExceededException(FlowForgeException):
    """Raised when an operation would exceed maximum capacity."""

    def __init__(self, current: int, limit: int, requested: int = 1):
        super().__init__(
            message=f"Capacity exceeded: {current}/{limit} seats filled. Cannot accommodate {requested} more.",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CAPACITY_EXCEEDED",
            details={"current_seats": current, "capacity_limit": limit, "requested": requested},
        )


class PaymentException(FlowForgeException):
    """Raised when a payment operation fails or is declined."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PAYMENT_ERROR",
            details=details,
        )


class PaymentVerificationException(FlowForgeException):
    """Raised when server-side payment verification fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="PAYMENT_VERIFICATION_FAILED",
            details=details,
        )


class AuthenticationException(FlowForgeException):
    """Raised when authentication credentials are invalid or missing."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details={"authenticate_header": "Bearer"},
        )


class AuthorizationException(FlowForgeException):
    """Raised when the authenticated user does not have permission."""

    def __init__(self, message: str = "Operation not permitted for this user"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class AIEngineException(FlowForgeException):
    """Raised when workflow generation via AI engine encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI Engine Error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="AI_ENGINE_ERROR",
            details=details,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application."""

    @app.exception_handler(FlowForgeException)
    async def flowforge_exception_handler(request: Request, exc: FlowForgeException):
        logger.warning(
            "FlowForge domain exception [%s] on %s: %s",
            exc.error_code,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for error in exc.errors():
            loc = " -> ".join(str(item) for item in error.get("loc", []))
            formatted_errors.append(f"{loc}: {error.get('msg', 'invalid value')}")
        logger.info("Request validation failed on %s: %s", request.url.path, formatted_errors)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the supplied parameters.",
                "details": {"errors": formatted_errors, "raw": exc.errors()},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {"status_code": exc.status_code},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled server error on %s: %s", request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact support.",
                "details": {},
            },
        )

