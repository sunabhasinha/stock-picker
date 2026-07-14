"""
Engine/session wiring. The database URL comes from the DATABASE_URL
environment variable (spec invariant: secrets via environment, never
committed). Supabase hands out `postgres://...` URLs; SQLAlchemy 2.0 with
the psycopg3 driver wants `postgresql+psycopg://...` - normalized here so
the Supabase string can be pasted verbatim.
"""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager

from sqlalchemy import create_engine, text
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


@contextmanager
def rls_transaction(factory: sessionmaker[Session], user_id: uuid.UUID):
    """
    One request's user-data transaction under the RLS enforcement chain
    (ADR-0006 clause 4): assume the non-owner app_rls role and set the
    transaction-local user id the M1 policies key on. SET LOCAL reverts
    automatically at transaction end - the elevated (owner) role never
    leaks past the request.

    On non-Postgres engines (the SQLite test suite) the SETs are skipped:
    those tests exercise application-level scoping (layer 1); the RLS
    layer (layer 2) is exercised against real Postgres (gated test) and
    in production.
    """
    session = factory()
    try:
        if session.get_bind().dialect.name == "postgresql":
            session.execute(text("SET LOCAL ROLE app_rls"))
            session.execute(
                text("SELECT set_config('app.user_id', :uid, true)"),
                {"uid": str(user_id)},
            )
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
