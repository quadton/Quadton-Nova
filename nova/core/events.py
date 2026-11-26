"""In-process event bus shared by all NOVA components.

Delivery is sequential and in subscription order: a slow handler delays the publisher. A handler
that raises is logged and skipped; it never stops other handlers or reaches the publisher.
Events are not persisted.
"""

from __future__ import annotations

import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

WILDCARD = "*"


@dataclass(frozen=True, slots=True)
class Event:
    """An immutable notification. Topics are dotted strings such as ``task.created``."""

    topic: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


Handler = Callable[[Event], Awaitable[None] | None]


class EventBus:
    """Publish/subscribe hub. Handlers may be plain functions or coroutine functions."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        """Register ``handler`` for ``topic`` (``"*"`` for all). Returns an unsubscribe callable."""
        self._handlers[topic].append(handler)

        def unsubscribe() -> None:
            handlers = self._handlers.get(topic, [])
            if handler in handlers:
                handlers.remove(handler)

        return unsubscribe

    async def publish(self, event: Event) -> None:
        """Deliver ``event`` to topic subscribers, then to wildcard subscribers."""
        if event.topic == WILDCARD:
            raise ValueError("cannot publish to the wildcard topic")
        handlers = [*self._handlers.get(event.topic, ()), *self._handlers.get(WILDCARD, ())]
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                logger.exception(
                    "event handler failed",
                    extra={
                        "topic": event.topic,
                        "handler": getattr(handler, "__qualname__", repr(handler)),
                    },
                )
