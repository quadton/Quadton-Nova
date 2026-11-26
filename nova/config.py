"""Application configuration, read from NOVA_* environment variables and an optional .env file."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR_NAME = "quadton-nova"


def default_data_dir() -> Path:
    """Return the per-user data directory for the current operating system."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP_DIR_NAME


class Settings(BaseSettings):
    """Runtime settings. Every field can be overridden with a NOVA_<FIELD> variable."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "production", "test"] = "development"
    data_dir: Path = Field(default_factory=default_data_dir)
    database_url: str | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = False
    log_to_file: bool = True

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    @field_validator("data_dir")
    @classmethod
    def _expand_data_dir(cls, value: Path) -> Path:
        return value.expanduser()

    @property
    def db_url(self) -> str:
        """SQLAlchemy URL: the explicit override, or nova.db inside the data directory."""
        if self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{(self.data_dir / 'nova.db').as_posix()}"

    @property
    def log_file(self) -> Path | None:
        """Path of the JSON log file, or None when file logging is disabled."""
        if not self.log_to_file:
            return None
        return self.data_dir / "logs" / "nova.log"

    def ensure_dirs(self) -> None:
        """Create the data and log directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file is not None:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
