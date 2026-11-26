import pytest
from pydantic import ValidationError

from nova.config import Settings


def test_database_url_defaults_to_file_in_data_dir(settings, tmp_path):
    assert settings.db_url == f"sqlite+aiosqlite:///{(tmp_path / 'nova.db').as_posix()}"


def test_database_url_override(tmp_path):
    custom = Settings(_env_file=None, data_dir=tmp_path, database_url="sqlite+aiosqlite:///x.db")
    assert custom.db_url == "sqlite+aiosqlite:///x.db"


def test_environment_variables_are_read(monkeypatch, tmp_path):
    monkeypatch.setenv("NOVA_LOG_LEVEL", "debug")
    monkeypatch.setenv("NOVA_LOG_JSON", "true")
    monkeypatch.setenv("NOVA_DATA_DIR", str(tmp_path))
    loaded = Settings(_env_file=None)
    assert loaded.log_level == "DEBUG"
    assert loaded.log_json is True
    assert loaded.data_dir == tmp_path


def test_invalid_log_level_is_rejected(tmp_path):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, data_dir=tmp_path, log_level="LOUD")


def test_ensure_dirs_creates_data_and_log_dirs(tmp_path):
    target = tmp_path / "nested" / "nova"
    Settings(_env_file=None, data_dir=target).ensure_dirs()
    assert target.is_dir()
    assert (target / "logs").is_dir()


def test_log_file_is_none_when_file_logging_is_disabled(tmp_path):
    assert Settings(_env_file=None, data_dir=tmp_path, log_to_file=False).log_file is None
