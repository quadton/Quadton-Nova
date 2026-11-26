import logging

import pytest

from nova.core.events import WILDCARD, Event, EventBus


async def test_sync_handler_receives_matching_event():
    bus = EventBus()
    received = []
    bus.subscribe("task.created", received.append)
    await bus.publish(Event("task.created", {"id": 1}))
    assert [event.payload for event in received] == [{"id": 1}]


async def test_async_handler_is_awaited():
    bus = EventBus()
    seen = []

    async def handler(event):
        seen.append(event.topic)

    bus.subscribe("task.done", handler)
    await bus.publish(Event("task.done"))
    assert seen == ["task.done"]


async def test_handler_is_not_called_for_other_topics():
    bus = EventBus()
    received = []
    bus.subscribe("a", received.append)
    await bus.publish(Event("b"))
    assert received == []


async def test_wildcard_receives_every_topic():
    bus = EventBus()
    topics = []
    bus.subscribe(WILDCARD, lambda event: topics.append(event.topic))
    await bus.publish(Event("a"))
    await bus.publish(Event("b"))
    assert topics == ["a", "b"]


async def test_failing_handler_is_logged_and_does_not_block_others(caplog):
    bus = EventBus()
    received = []

    def broken(event):
        raise RuntimeError("boom")

    bus.subscribe("t", broken)
    bus.subscribe("t", received.append)
    with caplog.at_level(logging.ERROR):
        await bus.publish(Event("t"))
    assert len(received) == 1
    assert "event handler failed" in caplog.text


async def test_unsubscribe_stops_delivery():
    bus = EventBus()
    received = []
    unsubscribe = bus.subscribe("t", received.append)
    unsubscribe()
    unsubscribe()  # calling twice is harmless
    await bus.publish(Event("t"))
    assert received == []


async def test_publishing_to_wildcard_topic_is_rejected():
    with pytest.raises(ValueError):
        await EventBus().publish(Event(WILDCARD))


def test_events_get_unique_ids():
    assert Event("t").id != Event("t").id
