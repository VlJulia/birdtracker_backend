import asyncio
import logging

from alembic import context

from app.core import models  # noqa: F401  регистрирует таблицы в Base.metadata
from app.core.database import Base, engine

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")

if context.is_offline_mode():
    raise SystemExit("Режим --sql не поддерживается")


def run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


async def main() -> None:
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


asyncio.run(main())
