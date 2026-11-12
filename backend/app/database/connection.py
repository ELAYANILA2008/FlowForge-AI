"""SQLAlchemy 2.x Engine and Connection Management.

Supports:
- PostgreSQL with psycopg driver (production and standard development)
- SQLite with thread isolation flags (for local automated test suites)
- Connection pooling with pre-ping validation to discard stale database connections
"""

import logging
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import StaticPool, QueuePool

from app.core.config import settings

logger = logging.getLogger("flowforge.database")


def create_db_engine(database_url: str) -> Engine:
    """Create a configured SQLAlchemy engine with appropriate connection pooling."""
    url_lower = database_url.lower()

    if "sqlite" in url_lower:
        # SQLite configuration for testing
        is_memory = ":memory:" in url_lower
        logger.info("Initializing SQLite engine for testing (in_memory=%s)", is_memory)
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool if is_memory else None,
            echo=False,
        )

    # PostgreSQL configuration with robust connection pooling
    logger.info("Initializing PostgreSQL engine via psycopg driver")
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_pre_ping=True,  # Discards stale or dropped connections automatically
        echo=settings.DEBUG and not settings.is_production(),
    )


# Global database engine instance initialized from environment configuration
engine: Engine = create_db_engine(settings.DATABASE_URL)

