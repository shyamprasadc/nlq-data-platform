"""
Database session management and dependency injection.
Provides database engine and session factory for the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings


# Create database engine
# For SQLite, we use check_same_thread=False to allow FastAPI's async nature
# For production PostgreSQL/MySQL, you would configure connection pooling here
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create SessionLocal class
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.

    This function is used as a FastAPI dependency to provide
    database sessions to route handlers.

    Usage in routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Database session

    Note:
        The session is automatically closed after the request completes,
        even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
