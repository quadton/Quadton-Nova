"""Async SQLite engine creation and database initialization."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from nova.db.base import SCHEMA_VERSION, Base, SchemaInfo

logger = logging.getLogger(__name__)

VERSION_KEY = "schema_version"


class SchemaVersionError(RuntimeError):
    """Raised when an existing database does not match this code's schema version."""


def create_engine(url: str) -> AsyncEngine:
    """Create an async engine. SQLite connections get foreign keys on and WAL journaling."""
    engine = create_async_engine(url)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragmas(dbapi_connection: Any, _record: Any) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
            finally:
                cursor.close()

    return engine


async def init_db(engine: AsyncEngine) -> None:
    """Create missing tables and record or check the schema version. Safe to call repeatedly."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session, session.begin():
        row = await session.get(SchemaInfo, VERSION_KEY)
        if row is None:
            session.add(SchemaInfo(key=VERSION_KEY, value=str(SCHEMA_VERSION)))
            logger.info("database initialized", extra={"schema_version": SCHEMA_VERSION})
        elif row.value != str(SCHEMA_VERSION):
            raise SchemaVersionError(
                f"database schema version is {row.value}, this NOVA build expects "
                f"{SCHEMA_VERSION}; migrations are not implemented yet"
            )
