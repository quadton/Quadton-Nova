import json

from nova.app import NovaApp
from nova.core.events import EventBus


async def test_startup_initializes_storage_logging_and_events(settings):
    bus = EventBus()
    topics = []
    bus.subscribe("*", lambda event: topics.append(event.topic))

    app = await NovaApp.create(settings, bus=bus)
    try:
        assert (settings.data_dir / "nova.db").is_file()
        assert topics == ["app.started"]
    finally:
        await app.close()

    assert topics == ["app.started", "app.stopping"]
    lines = settings.log_file.read_text(encoding="utf-8").splitlines()
    messages = [json.loads(line)["msg"] for line in lines]
    assert "NOVA started" in messages
    assert "NOVA stopped" in messages
