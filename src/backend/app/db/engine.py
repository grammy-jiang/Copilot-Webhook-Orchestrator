"""Database engine and session management."""

from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings


def get_engine() -> Engine:
    """Create and return the database engine."""
    settings = get_settings()
    connect_args = {}

    # SQLite-specific configuration
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args=connect_args,
    )


# Global engine instance (lazy initialization)
_engine: Engine | None = None


def get_global_engine() -> Engine:
    """Get or create the global engine instance."""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def init_db() -> None:
    """Initialize the database by creating all tables."""
    engine = get_global_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get a database session (FastAPI dependency)."""
    engine = get_global_engine()
    with Session(engine) as session:
        yield session
