"""Composition root: wires configuration, logging, storage, and events together."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncEngine

from nova import __version__
from nova.config import Settings
from nova.core.events import Event, EventBus
from nova.db.session import create_engine, init_db
from nova.logging_config import configure_logging, shutdown_logging

logger = logging.getLogger(__name__)


class NovaApp:
    """Holds the shared services. Build with ``NovaApp.create()``; release with ``close()``."""

    def __init__(self, settings: Settings, engine: AsyncEngine, bus: EventBus) -> None:
        self.settings = settings
        self.engine = engine
        self.bus = bus

    @classmethod
    async def create(
        cls, settings: Settings | None = None, bus: EventBus | None = None
    ) -> NovaApp:
        settings = settings or Settings()
        settings.ensure_dirs()
        configure_logging(
            settings.log_level, json_console=settings.log_json, log_file=settings.log_file
        )
        engine = create_engine(settings.db_url)
        try:
            await init_db(engine)
        except Exception:
            logger.exception("database initialization failed")
            await engine.dispose()
            shutdown_logging()
            raise

        app = cls(settings, engine, bus or EventBus())
        started = {"version": __version__, "environment": settings.environment}
        logger.info("NOVA started", extra=started)
        await app.bus.publish(Event("app.started", started))
        return app

    async def close(self) -> None:
        """Publish app.stopping, release the database, and close log files."""
        await self.bus.publish(Event("app.stopping"))
        await self.engine.dispose()
        logger.info("NOVA stopped")
        shutdown_logging()
