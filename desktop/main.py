"""Desktop entry point.

Phase 1 starts the application foundation only (settings, logging, database, events).
The PySide6 interface arrives in a later phase.
"""

import asyncio

from nova.app import NovaApp


async def _run() -> None:
    app = await NovaApp.create()
    try:
        print("QUADTON NOVA foundation ready.")
        print(f"  data dir: {app.settings.data_dir}")
        print(f"  database: {app.settings.db_url}")
    finally:
        await app.close()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
