"""Alembic environment: URL from DATABASE_URL, metadata from the ORM."""

from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.models import Base
from app.db.session import database_url

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """--sql mode: emit the SQL without a database connection. Used both
    for review and as the syntax gate in tests/CI."""
    context.configure(
        url=database_url() if not context.get_x_argument(as_dictionary=True).get("dry")
        else "postgresql+psycopg://dry-run-only",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
