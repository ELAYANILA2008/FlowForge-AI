"""Configuration module for FlowForge AI Engine.

Handles environment variables, API credentials, model configurations,
and safe logging without leaking sensitive credentials.
"""

import os
import logging
from typing import Optional

# Setup logger for the AI Engine
logger = logging.getLogger("flowforge.ai_engine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [FlowForge-AI]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def mask_api_key(key: Optional[str]) -> str:
    """Safely mask an API key for logs and error messages.
    
    Never exposes full API keys.
    e.g. sk-1234567890abcdef -> sk-...cdef
    """
    if not key:
        return "<NOT_SET>"
    trimmed = key.strip()
    if len(trimmed) <= 8:
        return "********"
    return f"{trimmed[:3]}...{trimmed[-4:]}"


class AIConfig:
    """Configuration class for AI engine parameters."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        use_mock: Optional[bool] = None,
    ):
        # 1. API Key resolution (parameter -> environment variable)
        self.api_key: Optional[str] = api_key or os.getenv("OPENAI_API_KEY")

        # 2. Model selection (default to gpt-4o-mini for fast, cost-effective structured output)
        self.model: str = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # 3. Timeout in seconds
        env_timeout = os.getenv("OPENAI_TIMEOUT")
        if timeout is not None:
            self.timeout: float = float(timeout)
        elif env_timeout:
            try:
                self.timeout = float(env_timeout)
            except ValueError:
                self.timeout = 30.0
        else:
            self.timeout = 30.0

        # 4. Max Retries on transient errors
        env_retries = os.getenv("OPENAI_MAX_RETRIES")
        if max_retries is not None:
            self.max_retries: int = int(max_retries)
        elif env_retries:
            try:
                self.max_retries = int(env_retries)
            except ValueError:
                self.max_retries = 2
        else:
            self.max_retries = 2

        # 5. Mock mode determination:
        # Explicit flag takes precedence; otherwise auto-mock if no API key is set
        # or if FLOWFORGE_AI_MOCK environment variable is 'true' or '1'.
        env_mock = os.getenv("FLOWFORGE_AI_MOCK", "").lower() in ("true", "1", "yes")
        if use_mock is not None:
            self.use_mock: bool = use_mock
        elif env_mock:
            self.use_mock = True
        elif not self.api_key:
            self.use_mock = True
        else:
            self.use_mock = False

    def log_status(self) -> None:
        """Log safe status of configuration without leaking sensitive keys."""
        logger.info(
            "AI Engine Config initialized | Model: %s | Mock Mode: %s | Timeout: %.1fs | Key: %s",
            self.model,
            self.use_mock,
            self.timeout,
            mask_api_key(self.api_key),
        )

