from __future__ import annotations

from sqlalchemy import text

from ..database import get_engine


class DatabaseHealthRepository:
    """Database reachability lives in repositories so SQL never leaks into services/routes."""

    def ping(self) -> bool:
        try:
            with get_engine().connect() as connection:
                connection.execute(text('SELECT 1'))
            return True
        except Exception:
            return False
