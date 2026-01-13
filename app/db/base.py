"""
SQLAlchemy declarative base and model imports.
All models must be imported here for Alembic migrations to work correctly.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base
# All SQLAlchemy models will inherit from this
Base = declarative_base()

# Import all models here so Alembic can detect them
# This ensures migrations include all tables
# Uncomment when models are created:
# from app.models.user import User
# from app.models.document import Document
