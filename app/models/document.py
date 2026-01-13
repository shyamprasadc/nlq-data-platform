"""
Document database model.
Represents documents/content that can be processed by AI/LLM services.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Document(Base):
    """
    Document model for storing AI-processable content.

    This model is designed to store documents that can be:
    - Processed by LLM services
    - Embedded for vector search
    - Associated with user accounts

    Attributes:
        id: Primary key
        title: Document title
        content: Main document content (text)
        user_id: Foreign key to users table
        metadata: JSON field for flexible metadata storage
        created_at: Timestamp of document creation
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # JSON field for flexible metadata
    # Can store: embeddings, tags, processing status, etc.
    meta_data = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship to User model
    # Uncomment when you want to use relationships:
    # user = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title})>"
