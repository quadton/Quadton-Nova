# QUADTON NOVA

Cross-platform AI desktop assistant and autonomous agent system for Windows and Linux. The long-term goal is a personal AI operating environment: assistant, coding agent, desktop automation, file manager, web research, and a visual workflow builder, all behind explicit permission checks.

## Status

This repository is at the end of Phase 1 (project foundation). The foundation is written but has not yet had its first verified run; see [DEVELOPMENT.md](DEVELOPMENT.md) for the exact verification steps and current state.

What exists:

- Application settings (Pydantic) with `NOVA_*` environment overrides.
- Structured logging (console text or JSON, rotating JSON log file).
- Async SQLite database initialization with a schema version guard.
- An in-process event bus.
- Pytest suites (unit, integration, platform), a Linux and Windows GitHub Actions workflow, and a Codespaces dev container.
- A minimal Next.js shell for the optional remote dashboard.

What does not exist yet: AI providers, orchestrator, agents, tools, memory, the PySide6 interface, desktop automation, workflows, the remote dashboard features. Nothing in this list should be assumed to work.

## Technology stack

Phase 1 uses Python 3.12+, Pydantic and pydantic-settings, SQLAlchemy 2 (async) with aiosqlite, pytest, ruff, and GitHub Actions. The dashboard shell uses Next.js, React, and TypeScript. The full planned stack (PySide6, FastAPI, Playwright, React Flow, container sandboxing) is described in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and is added phase by phase.

## Getting started

### GitHub Codespaces (recommended)

1. Open the repository in a Codespace. The dev container installs Python dependencies and the dashboard shell automatically.
2. Run the checks:

   ```bash
   ruff check .
   pytest
   python apps/desktop/main.py
   ```

### Local machine

```bash
python -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Configuration

Copy `.env.example` to `.env` to override defaults. All variables are optional.

| Variable | Default | Meaning |
| --- | --- | --- |
| `NOVA_ENVIRONMENT` | `development` | `development`, `production`, or `test` |
| `NOVA_DATA_DIR` | per-OS user data dir | Where the database and logs live |
| `NOVA_DATABASE_URL` | SQLite file in the data dir | SQLAlchemy URL override |
| `NOVA_LOG_LEVEL` | `INFO` | `DEBUG` to `CRITICAL` |
| `NOVA_LOG_JSON` | `false` | JSON lines on the console |
| `NOVA_LOG_TO_FILE` | `true` | Write `logs/nova.log` in the data dir |

The default data directory is `%APPDATA%\quadton-nova` on Windows and `$XDG_DATA_HOME/quadton-nova` (or `~/.local/share/quadton-nova`) on Linux.

Secrets such as AI provider keys are never hardcoded. They arrive in Phase 2 and are read from environment variables or the OS keyring.

## Repository layout

```
apps/desktop/      desktop entry point (UI comes later)
apps/dashboard/    Next.js shell for the optional remote dashboard
nova/              application package: config, logging, core, db
tests/             unit, integration, platform
docs/              architecture notes
.devcontainer/     Codespaces environment
.github/workflows/ CI for Linux and Windows
```
