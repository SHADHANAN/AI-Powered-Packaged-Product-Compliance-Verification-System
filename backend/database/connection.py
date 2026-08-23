from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from backend.config import get_settings


class Base(DeclarativeBase):
    """
    Base declarative class for all SQLAlchemy 2.x models.
    """
    pass


def get_engine_args(database_url: str) -> dict:
    """
    Generates appropriate engine arguments depending on dialect (PostgreSQL vs SQLite).
    """
    settings = get_settings()
    engine_kwargs = {
        "echo": settings.DEBUG,
    }

    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs.update({
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_pre_ping": settings.DB_POOL_PRE_PING,
            "pool_recycle": getattr(settings, "DB_POOL_RECYCLE", 1800),
        })

    return engine_kwargs


def create_db_engine(database_url: str = None):
    """
    Creates and returns a SQLAlchemy engine configured from settings or argument.
    """
    settings = get_settings()
    db_url = database_url or settings.DATABASE_URL
    eng = create_engine(db_url, **get_engine_args(db_url))

    if db_url.startswith("sqlite"):
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return eng


engine = create_db_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures session is properly closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
