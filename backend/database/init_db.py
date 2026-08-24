from backend.database.connection import Base, engine, create_db_engine
from backend.database.models import (
    Product,
    Verification,
    ExtractedField,
    ComplianceCheck,
)
from backend.utils.logger import logger


def init_database(engine_to_use=None) -> None:
    """
    Initializes database tables using SQLAlchemy metadata.
    This function is called manually or by migration/setup scripts.
    It does not execute automatically during FastAPI application startup.
    """
    active_engine = engine_to_use or engine
    logger.info("Creating database tables using SQLAlchemy metadata...")
    Base.metadata.create_all(bind=active_engine)
    logger.info("Database tables initialized successfully.")


if __name__ == "__main__":
    init_database()
