# net/api/db.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

# SQLite file in project: net/ohsupath.db (override with DB_PATH env)
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "ohsupath.db"
DB_PATH = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Single engine for the whole app
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + threads
    pool_pre_ping=True,
)

def init_db() -> None:
    """Apply basic SQLite pragmas and create tables."""
    with engine.connect() as conn:
        # Safe, no-op on non-SQLite dialects; here we are SQLite.
        conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
        conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
    SQLModel.metadata.create_all(engine)

def get_db() -> Iterator[Session]:
    """
    FastAPI dependency: yields a SQLModel Session bound to our engine.
    Usage in routers:
        from ..db import get_db
        @router.get("/...")
        def endpoint(..., db: Session = Depends(get_db)):
            ...
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
