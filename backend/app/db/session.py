"""Database session management.

We expose:
- `engine`: a lazily-configured SQLAlchemy engine
- `SessionLocal`: a session factory
- `get_db`: a FastAPI dependency that yields a session and closes it

Keeping this file tiny and focused makes it easy to swap engines or
add read replicas later.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # detect dead connections up front
    pool_size=10,
    max_overflow=20,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
