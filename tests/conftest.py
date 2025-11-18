from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

# Ensure the testing environment variables are loaded before importing the app.
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env.test", override=False)
os.environ.setdefault("ENVIRONMENT", "TEST")

from src.config import system_config  # noqa: E402
from src.database import load_models  # noqa: E402
from src.database.base_model import Base  # noqa: E402
from src.database.core import engine, session as session_factory  # noqa: E402
from src.main import app  # noqa: E402

load_models()


def _metadata_table_names() -> list[str]:
    if not Base.metadata.tables:
        return []
    return [table.name for table in Base.metadata.sorted_tables]


async def _truncate_all_tables(async_engine: AsyncEngine) -> None:
    table_names = _metadata_table_names()
    if not table_names:
        return

    formatted = ", ".join(f'"{name}"' for name in table_names)
    async with async_engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE {formatted} RESTART IDENTITY CASCADE")
        )


@pytest.fixture(scope="session")
def alembic_config() -> AlembicConfig:
    cfg = AlembicConfig(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", system_config.ALEMBIC_DATABASE_URL)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(alembic_config: AlembicConfig):
    """
    Ensure the testing database schema is up-to-date before running tests.
    """
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def clean_database(async_engine: AsyncEngine, apply_migrations):
    """
    Truncate every domain table before and after each test to guarantee isolation.
    """
    await _truncate_all_tables(async_engine)
    yield
    await _truncate_all_tables(async_engine)


@pytest_asyncio.fixture(loop_scope="session")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
        finally:
            if session.in_transaction():
                await session.rollback()
            await session.close()


@pytest_asyncio.fixture(loop_scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client
