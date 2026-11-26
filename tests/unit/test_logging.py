import json
import logging
import sys

import pytest

from nova.logging_config import JsonFormatter, configure_logging, shutdown_logging


def _record(extra=None, exc_info=None):
    logger = logging.getLogger("nova.test")
    return logger.makeRecord(
        "nova.test", logging.INFO, __file__, 1, "hello %s", ("world",), exc_info, extra=extra
    )


@pytest.fixture
def clean_logging():
    yield
    shutdown_logging()


def test_json_formatter_outputs_core_fields_and_extras():
    data = json.loads(JsonFormatter().format(_record(extra={"task_id": "t1"})))
    assert data["msg"] == "hello world"
    assert data["level"] == "INFO"
    assert data["logger"] == "nova.test"
    assert data["fields"] == {"task_id": "t1"}
    assert "ts" in data


def test_json_formatter_omits_fields_when_there_are_no_extras():
    assert "fields" not in json.loads(JsonFormatter().format(_record()))


def test_json_formatter_includes_exception_text():
    try:
        raise ValueError("boom")
    except ValueError:
        exc_info = sys.exc_info()
    data = json.loads(JsonFormatter().format(_record(exc_info=exc_info)))
    assert "ValueError: boom" in data["exc"]


def test_configure_logging_writes_json_lines_to_file(tmp_path, clean_logging):
    log_file = tmp_path / "logs" / "nova.log"
    configure_logging("INFO", log_file=log_file)
    logging.getLogger("nova.test").info("written", extra={"k": "v"})
    shutdown_logging()
    data = json.loads(log_file.read_text(encoding="utf-8").splitlines()[-1])
    assert data["msg"] == "written"
    assert data["fields"] == {"k": "v"}


def test_configure_logging_filters_by_level(tmp_path, clean_logging):
    log_file = tmp_path / "nova.log"
    configure_logging("WARNING", log_file=log_file)
    logging.getLogger("nova.test").info("quiet")
    logging.getLogger("nova.test").warning("loud")
    shutdown_logging()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["msg"] for line in lines] == ["loud"]


def test_configure_logging_replaces_earlier_handlers(tmp_path, clean_logging):
    configure_logging("INFO", log_file=tmp_path / "a.log")
    configure_logging("INFO", log_file=tmp_path / "a.log")
    assert len(logging.getLogger("nova").handlers) == 2  # one console, one file
