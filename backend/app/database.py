"""
Database session setup.

Why this lives in its own module, separate from models/ and schemas/:
SQLAlchemy's "engine" and "Session" represent the connection to the
database itself, not any particular table. Keeping that concern isolated
means models/ (ORM table definitions) and schemas/ (Pydantic request and
response shapes) each stay focused on their own job, and this module can be
reused or swapped out (e.g. for a test database) independently once tests
are introduced.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class every ORM model in app/models/ will inherit from.
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
