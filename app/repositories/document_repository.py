"""
Document repository for database operations.
Handles all database queries related to documents.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.ai import DocumentCreate, DocumentUpdate


class DocumentRepository:
    """
    Repository for Document model database operations.

    Encapsulates all database queries for documents,
    separating data access from business logic.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieve a document by ID.

        Args:
            document_id: Document's primary key

        Returns:
            Document object if found, None otherwise
        """
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Retrieve all documents for a specific user.

        Args:
            user_id: User's primary key
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Document objects
        """
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, user_id: int, document_data: DocumentCreate) -> Document:
        """
        Create a new document.

        Args:
            user_id: Owner's user ID
            document_data: Document creation data

        Returns:
            Created Document object
        """
        db_document = Document(
            title=document_data.title,
            content=document_data.content,
            user_id=user_id,
            meta_data=document_data.meta_data,
        )

        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)

        return db_document

    def update(
        self, document_id: int, document_data: DocumentUpdate
    ) -> Optional[Document]:
        """
        Update an existing document.

        Args:
            document_id: Document's primary key
            document_data: Updated document data

        Returns:
            Updated Document object if found, None otherwise
        """
        db_document = self.get_by_id(document_id)

        if not db_document:
            return None

        # Update only provided fields
        update_data = document_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_document, field, value)

        self.db.commit()
        self.db.refresh(db_document)

        return db_document

    def delete(self, document_id: int) -> bool:
        """
        Delete a document.

        Args:
            document_id: Document's primary key

        Returns:
            True if deleted, False if not found
        """
        db_document = self.get_by_id(document_id)

        if not db_document:
            return False

        self.db.delete(db_document)
        self.db.commit()

        return True

    def count_by_user(self, user_id: int) -> int:
        """
        Count documents for a specific user.

        Args:
            user_id: User's primary key

        Returns:
            Document count for the user
        """
        return self.db.query(Document).filter(Document.user_id == user_id).count()
