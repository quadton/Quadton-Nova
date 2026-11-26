# Development status

## Current phase

Phase 1, project foundation: implemented, awaiting first verified run.

All Phase 1 files were written in an environment with no network access, so the Pydantic and SQLAlchemy code and the full pytest suite have not been executed. Only the standard-library parts (event bus, logging) were smoke-tested, and all Python files were syntax-checked. Treat Phase 1 as unverified until the steps below pass.

## Verify Phase 1

1. Push to GitHub as `quadton-nova` and open it in a Codespace. The post-create step must finish without manual intervention.
2. In the Codespace: `ruff check .` then `pytest`. Both must pass.
3. `python apps/desktop/main.py` must print the data directory and database path and exit cleanly. Run it twice; the second run must also succeed.
4. Open a pull request and confirm the GitHub Actions workflow is green on both `ubuntu-latest` and `windows-latest`.
5. In `apps/dashboard`, run `npm install` then `npm run dev` and open the forwarded port 3000. Commit the generated `package-lock.json`.
6. Record results here and tag `phase-1`.

## Completed (pending verification)

- Project layout, `pyproject.toml`, `.env.example`, `.gitignore`.
- Settings with `NOVA_*` overrides and per-OS data directory.
- Structured logging with a JSON file log.
- Async SQLite initialization with schema version guard.
- In-process event bus.
- Composition root (`NovaApp`) and a desktop entry point that starts the foundation.
- Pytest suites and CI for Linux and Windows.
- Codespaces dev container.
- Minimal dashboard shell.

## In progress

Nothing.

## Outstanding bugs

None known. None could have been observed yet because nothing has run.

## Known limitations

- No migrations. The database stores a schema version and refuses to open a mismatching database. Add Alembic before the first Phase 2 tables.
- Logs have no secret redaction. Phase 1 handles no secrets; add redaction before provider keys exist.
- The event bus is in-process, delivers sequentially, and does not persist events.
- PySide6 is not a dependency yet, and Codespaces has no display to run it. The desktop UI can only be exercised on a Windows or Linux machine.
- The dev container has no Docker-in-Docker. Add the `docker-in-docker` feature in Phase 3 when sandboxed execution lands. GitHub's Windows runners cannot run Linux containers, so sandbox integration tests will be Linux-only.
- CI does not build the dashboard yet, and the dashboard has no lockfile.
- Ruff runs the `E`, `F`, `UP`, `B` rule sets. The first CI run may flag style issues.
- No LICENSE file has been chosen.

## Next steps

1. Run the verification steps above and fix whatever fails.
2. Add Alembic migrations and a `gitleaks` pre-commit hook and CI step.
3. Phase 2, NOVA Core: provider abstraction (one OpenAI-compatible adapter covering OpenAI, OpenRouter, Gemini, and Ollama, plus an Anthropic adapter), orchestrator, deny-by-default permission checks enforced in code, tool registry where each tool returns a result plus a postcondition check, persistent memory, task states, and a per-task token and cost cap.
4. Decide whether to build the dashboard right after Phase 2, since it is the only interface runnable from an iPad.
