import os
from pathlib import Path

import pytest

from nova.config import Settings


@pytest.fixture(autouse=True)
def _clean_nova_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the developer's own NOVA_* variables from leaking into tests."""
    for name in [name for name in os.environ if name.startswith("NOVA_")]:
        monkeypatch.delenv(name)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Settings that store everything under a temporary directory and ignore any .env file."""
    return Settings(_env_file=None, data_dir=tmp_path)
