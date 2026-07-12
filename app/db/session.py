"""
Engine/session wiring. The database URL comes from the DATABASE_URL
environment variable (spec invariant: secrets via environment, never
committed). Supabase hands out `postgres://...` URLs; SQLAlchemy 2.0 with
the psycopg3 driver wants `postgresql+psycopg://...` - normalized here so
the Supabase string can be pasted verbatim.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Point it at your Supabase (or local) "
            "Postgres, e.g. postgresql://user:pass@host:5432/postgres"
        )
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def make_engine(url: str | None = None):
    return create_engine(url or database_url())


def make_session_factory(url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=make_engine(url), expire_on_commit=False)
