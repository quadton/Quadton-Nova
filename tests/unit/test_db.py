import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nova.db.base import SCHEMA_VERSION, SchemaInfo
from nova.db.session import VERSION_KEY, SchemaVersionError, create_engine, init_db


@pytest.fixture
async def engine(tmp_path):
    engine = create_engine(f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}")
    yield engine
    await engine.dispose()


async def test_init_db_creates_schema_and_records_version(engine):
    await init_db(engine)
    async with AsyncSession(engine) as session:
        row = await session.get(SchemaInfo, VERSION_KEY)
    assert row is not None
    assert row.value == str(SCHEMA_VERSION)


async def test_init_db_is_idempotent(engine):
    await init_db(engine)
    await init_db(engine)
    async with AsyncSession(engine) as session:
        rows = (await session.scalars(select(SchemaInfo))).all()
    assert len(rows) == 1


async def test_init_db_rejects_unknown_schema_version(engine):
    await init_db(engine)
    async with AsyncSession(engine) as session, session.begin():
        row = await session.get(SchemaInfo, VERSION_KEY)
        assert row is not None
        row.value = "999"
    with pytest.raises(SchemaVersionError):
        await init_db(engine)


async def test_sqlite_pragmas_are_applied(engine):
    async with engine.connect() as conn:
        foreign_keys = (await conn.exec_driver_sql("PRAGMA foreign_keys")).scalar_one()
        journal_mode = (await conn.exec_driver_sql("PRAGMA journal_mode")).scalar_one()
    assert foreign_keys == 1
    assert journal_mode == "wal"
