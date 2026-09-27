from __future__ import annotations

import os
import re
from collections.abc import Generator
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Default SQLite database path for local dev/testing if PostgreSQL is not specified
DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[3] / ".landsync-data.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

DATABASE_URL = re.sub(r"^postgres(ql)?://", "postgresql+psycopg://", os.getenv("DATABASE_URL", DEFAULT_DB_URL))

# SQLite concurrency kwargs vs PostgreSQL pooling
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize PostGIS extension (if Postgres) and create all tables."""
    if not DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
            except Exception:
                # User might not have SUPERUSER; continue gracefully
                pass
    Base.metadata.create_all(bind=engine)
