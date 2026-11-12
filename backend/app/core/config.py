"""Core application configuration using Pydantic Settings.

Reads environment variables from backend/.env and provides type-safe
application settings with sensible defaults for development and testing.
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_DEFAULT_SECRET_KEY = "flowforge_super_secret_dev_key_at_least_32_characters_long"


class Settings(BaseSettings):
    """Centralized application settings for FlowForge AI backend."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Metadata
    APP_NAME: str = "FlowForge AI API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Cross-Origin Resource Sharing (CORS)
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/flowforge",
        description="SQLAlchemy database connection URL",
    )

    @property
    def is_sqlite(self) -> bool:
        """Return True if configured database is SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()

    # Security & JWT Authentication
    SECRET_KEY: str = Field(
        default=DEV_DEFAULT_SECRET_KEY,
        description="Secret key used for signing JWT access tokens and password salts",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI Engine & OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_ENGINE_USE_MOCK: bool = True

    # PayPal Sandbox Configuration (Orders API v2)
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_BASE_URL: str = "https://api-m.sandbox.paypal.com"
    PAYPAL_WEBHOOK_ID: Optional[str] = None

    # Email Delivery (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@flowforge.ai"
    SMTP_FROM_NAME: str = "FlowForge AI Operations"
    EMAIL_ENABLED: bool = False

    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.ENVIRONMENT.lower() == "production"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce production security rules on startup."""
        if self.is_production():
            if not self.SECRET_KEY or self.SECRET_KEY == DEV_DEFAULT_SECRET_KEY:
                raise ValueError(
                    "Production startup rejected: The default development SECRET_KEY is not permitted "
                    "when ENVIRONMENT=production. Provide a securely configured SECRET_KEY via backend/.env "
                    "or environment variables."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    f"Production startup rejected: SECRET_KEY must be at least 32 characters long. "
                    f"Current length is {len(self.SECRET_KEY)} characters."
                )
        return self

    def get_masked_secret(self, secret: Optional[str]) -> str:
        """Mask a sensitive credential for logging."""
        if not secret:
            return "<not configured>"
        if len(secret) <= 8:
            return "********"
        return f"{secret[:4]}...{secret[-4:]}"


# Global settings singleton
settings = Settings()

