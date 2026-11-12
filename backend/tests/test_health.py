"""Unit tests for FastAPI initialization, configuration, root, and health endpoints."""

import sys
import os
import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, root, health_check
from app.core.config import settings
from app.utils.currency import (
    normalize_currency,
    to_decimal_amount,
    format_currency_display,
    CurrencyRevenueBreakdown,
)
from decimal import Decimal


def test_app_initialization():
    """Verify that FastAPI app initializes with configured metadata and routes."""
    assert app.title == settings.APP_NAME
    assert app.version == settings.APP_VERSION

    # Check that route paths exist in routing table
    routes = [getattr(route, "path", "") for route in app.routes if hasattr(route, "path")]
    assert "/" in routes
    assert "/health" in routes
    assert f"{settings.API_V1_PREFIX}/health" in routes


def test_root_endpoint_data():
    """Verify that root() returns valid service identification and status."""
    data = root()
    assert isinstance(data, dict)
    assert data["name"] == settings.APP_NAME
    assert data["status"] == "online"
    assert data["version"] == settings.APP_VERSION
    assert data["api_v1"] == settings.API_V1_PREFIX
    assert "timestamp" in data


def test_health_check_endpoint_data():
    """Verify that health_check() returns healthy status and system metadata."""
    data = health_check()
    assert isinstance(data, dict)
    assert data["status"] == "healthy"
    assert data["service"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert "database" in data
    assert "integrations" in data
    assert data["integrations"]["ai_engine"] in ["mock", "openai"]


def test_cors_configuration():
    """Verify that CORS origins setting contains expected frontend origins."""
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_currency_utilities():
    """Verify currency validation, formatting, and decimal segregation."""
    assert normalize_currency("usd") == "USD"
    assert normalize_currency("eur") == "EUR"
    assert normalize_currency("inr") == "INR"

    with pytest.raises(ValueError):
        normalize_currency("GBP")

    amt = to_decimal_amount("20.50")
    assert isinstance(amt, Decimal)
    assert str(amt) == "20.50"

    assert format_currency_display(Decimal("20.00"), "USD") == "$20.00"
    assert format_currency_display(Decimal("30.00"), "EUR") == "€30.00"
    assert format_currency_display(Decimal("500.00"), "INR") == "₹500.00"

    breakdown = CurrencyRevenueBreakdown()
    breakdown.add("20.00", "USD")
    breakdown.add("500.00", "INR")
    breakdown.add("30.00", "EUR")

    res = breakdown.to_dict()
    assert res["totalRevenueUsd"] == 20.0
    assert res["totalRevenueInr"] == 500.0
    assert res["totalRevenueEur"] == 30.0
