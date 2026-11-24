import logging

from alembic import context

from app import models  # noqa: F401  регистрирует таблицы в Base.metadata
from app.database import Base, engine

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")

if context.is_offline_mode():
    raise SystemExit("Режим --sql не поддерживается")

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
