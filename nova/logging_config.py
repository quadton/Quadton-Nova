"""Structured logging for NOVA.

NOVA modules log through the standard library under the ``nova`` logger namespace. This module
attaches handlers to that namespace only, so third-party loggers are left untouched.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
from datetime import UTC, datetime
from pathlib import Path

ROOT_LOGGER_NAME = "nova"
_HANDLER_MARK = "_nova_handler"
_TEXT_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """Format each record as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        fields = {key: value for key, value in record.__dict__.items() if key not in _RESERVED}
        if fields:
            payload["fields"] = fields
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(
    level: str = "INFO",
    *,
    json_console: bool = False,
    log_file: Path | None = None,
) -> None:
    """Attach console and optional rotating-file handlers to the ``nova`` logger.

    Safe to call repeatedly: handlers from earlier calls are replaced. The file handler always
    writes JSON lines; the console handler writes readable text unless ``json_console`` is set.
    """
    shutdown_logging()
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(level.upper())
    logger.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(JsonFormatter() if json_console else logging.Formatter(_TEXT_FORMAT))
    _install(logger, console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(JsonFormatter())
        _install(logger, file_handler)


def shutdown_logging() -> None:
    """Remove and close the handlers installed by configure_logging, and reset the logger."""
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    for handler in list(logger.handlers):
        if getattr(handler, _HANDLER_MARK, False):
            logger.removeHandler(handler)
            handler.close()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


def _install(logger: logging.Logger, handler: logging.Handler) -> None:
    setattr(handler, _HANDLER_MARK, True)
    logger.addHandler(handler)
