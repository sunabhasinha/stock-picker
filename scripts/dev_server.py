"""Demo/dev server: the full product (SPA + auth + API) against a
THROWAWAY in-memory SQLite database - no DATABASE_URL, no Supabase, no
secrets. Data vanishes on restart. Verification/reset links print to
this terminal (dev email transport).

    python3 scripts/dev_server.py            # http://127.0.0.1:8000/

For the real database, run instead:  uvicorn app.server:app --port 8000
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.server import create_app

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(engine)
PORT = int(os.environ.get("PORT", "8000"))
app = create_app(
    session_factory=sessionmaker(bind=engine, expire_on_commit=False),
    base_url=f"http://127.0.0.1:{PORT}",  # keeps the origin check honest
)

if __name__ == "__main__":
    print("DEMO MODE: in-memory SQLite - data is NOT persisted.")
    uvicorn.run(app, host="127.0.0.1", port=PORT)
