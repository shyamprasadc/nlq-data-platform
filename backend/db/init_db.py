"""
Database initialization utilities.
Handles database table creation and initial setup.
"""

from backend.db.base import Base
from backend.db.session import engine
from backend.core.logging import get_logger

logger = get_logger(__name__)


def init_db() -> None:
    """
    Initialize the database.

    Creates all tables defined in SQLAlchemy models.
    This is a simple approach for development.

    For production, you should use Alembic migrations instead:
    - alembic init alembic
    - alembic revision --autogenerate -m "Initial migration"
    - alembic upgrade head
    """
    try:
        # Import all models before creating tables
        # This ensures all models are registered with Base.metadata
        from backend.models.user import User
        from backend.models.document import Document

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
