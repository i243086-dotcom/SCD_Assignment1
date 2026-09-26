from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from .config import get_settings

_engine: Engine | None = None


def get_engine() -> Engine:
    """Create the SQLAlchemy engine lazily so importing the application has no DB side effect."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    return _engine


def SessionLocal() -> Session:  # noqa: N802 - retained as the repository's documented session factory name
    return Session(bind=get_engine(), autoflush=False, expire_on_commit=False)


def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
