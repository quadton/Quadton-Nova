# Architecture

## Layers

NOVA is split into layers with one-way dependencies from top to bottom.

1. Desktop interface (PySide6): chat, task monitoring, settings, workflow views. Planned.
2. NOVA Core: orchestrator, planner, permission checks, task state, result verification. Planned for Phase 2; only the event bus exists today.
3. Agents: assistant, coding, and research agents that the orchestrator delegates to. Planned.
4. Tools: controlled access to files, terminal, browser, desktop, database, and workflows. Planned.
5. Platform adapters: Windows and Linux implementations behind common interfaces, so the core never imports an OS-specific API. Planned for Phase 6.
6. Persistent storage: SQLite through SQLAlchemy. Initialization exists today.

The optional remote dashboard is a separate client. The desktop instance stays the execution host and connects outward to a relay; the local machine is never exposed directly. This is Phase 8 and is not designed in detail yet.

## What Phase 1 implements

| Module | Responsibility |
| --- | --- |
| `nova/config.py` | `Settings` (Pydantic), per-OS default data directory, derived database URL and log path |
| `nova/logging_config.py` | Text and JSON formatters, rotating file handler, attached to the `nova` logger namespace only |
| `nova/db/base.py` | Declarative base, `schema_info` table, `SCHEMA_VERSION` |
| `nova/db/session.py` | Async engine factory with SQLite pragmas, `init_db`, `SchemaVersionError` |
| `nova/core/events.py` | `Event` and `EventBus` |
| `nova/app.py` | `NovaApp`: creates and releases the shared services in a fixed order |
| `apps/desktop/main.py` | Starts and stops `NovaApp`; the UI arrives later |

Startup order is settings, directories, logging, engine, `init_db`, then the `app.started` event. Shutdown publishes `app.stopping`, disposes the engine, then closes log files.

## Decisions

- **Async SQLAlchemy with aiosqlite.** The orchestrator and tools are asynchronous, and mixing sync database calls into them blocks the event loop.
- **Schema version guard instead of migrations for now.** `init_db` creates missing tables, stores a version, and refuses a database with a different version. Alembic replaces this before Phase 2 adds tables.
- **Logging under the `nova` namespace.** Third-party loggers are not reconfigured. The file log is always JSON for machine reading; the console is readable text unless `NOVA_LOG_JSON` is set. `shutdown_logging` closes file handles, which matters on Windows where open files cannot be deleted.
- **Sequential event delivery with isolated handler failures.** Deterministic ordering is easier to test and reason about. A broken handler is logged and skipped.
- **Per-OS data directory without a dependency.** Windows uses `%APPDATA%`; everything else follows XDG. The platform tests fake `sys.platform` so both branches run on both CI runners.
- **Optional extras not installed yet.** PySide6, FastAPI, Playwright, and the others are added in the phase that first uses them, to keep the dependency set minimal.
- **`db/` beside the planned `memory/`.** Database plumbing is shared infrastructure; `nova/memory/` will hold memory logic built on it.
- **Dev container from the stock Python image plus the Node feature.** No Dockerfile is needed until Phase 3 requires extra system packages or Docker-in-Docker.

## Planned layout

The full target structure (agents, providers, tools, workflows, automation adapters, API, files) follows the project specification. Directories are created in the phase that fills them rather than as empty stubs.
