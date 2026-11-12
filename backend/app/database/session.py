"""Database session management and FastAPI dependency injection.

Provides:
- SessionLocal factory configured for transaction-safe operations
- get_db generator for route-level dependency injection with automatic error rollback
- Schema initialization helper (init_db)
"""

import logging
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Engine

from app.database.connection import engine
from app.database.base import Base

logger = logging.getLogger("flowforge.database.session")

# Session factory bound to global engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding an isolated database session per request.
    
    Automatically rolls back uncommitted transactions if an unhandled exception occurs,
    and closes the session when the request context completes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        logger.warning("Rolling back uncommitted database transaction due to error: %s", str(exc))
        db.rollback()
        raise
    finally:
        db.close()


def init_db(target_engine: Engine = engine) -> None:
    """Create all registered database tables in the target database."""
    # Ensure all models are imported and registered with Base.metadata
    import app.models  # noqa: F401
    logger.info("Synchronizing database schema with SQLAlchemy models")
    Base.metadata.create_all(bind=target_engine)


def reset_db(target_engine: Engine = engine) -> None:
    """Drop and recreate all registered database tables (used during automated tests)."""
    import app.models  # noqa: F401
    logger.warning("Dropping and recreating all database tables")
    Base.metadata.drop_all(bind=target_engine)
    Base.metadata.create_all(bind=target_engine)

