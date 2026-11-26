"""The default data directory must resolve correctly on both supported operating systems.

These tests fake the platform, so they run on every CI runner.
"""

import sys
from pathlib import Path

from nova.config import default_data_dir


def test_windows_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert default_data_dir() == tmp_path / "quadton-nova"


def test_windows_falls_back_to_home_when_appdata_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert default_data_dir() == tmp_path / "AppData" / "Roaming" / "quadton-nova"


def test_linux_uses_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert default_data_dir() == tmp_path / "quadton-nova"


def test_linux_falls_back_to_local_share(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert default_data_dir() == tmp_path / ".local" / "share" / "quadton-nova"
