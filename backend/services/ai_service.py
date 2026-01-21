"""
AI service for coordinating AI operations.
Combines LLM service with document management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.repositories.document_repository import DocumentRepository
from backend.services.llm_service import LLMService
from backend.schemas.ai import (
    AIPromptRequest,
    AIResponse,
    Document,
    DocumentCreate,
    DocumentUpdate,
)
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AIService:
    """
    Service layer for AI-related business logic.

    Coordinates between:
    - LLM service for AI generation
    - Document repository for storage
    - Other services as needed
    """

    def __init__(self, db: Session):
        """
        Initialize AI service.

        Args:
            db: SQLAlchemy database session
        """
        self.document_repository = DocumentRepository(db)
        self.llm_service = LLMService()

    async def generate_ai_response(
        self, request: AIPromptRequest, user_id: Optional[int] = None
    ) -> AIResponse:
        """
        Generate an AI response and optionally save it.

        Args:
            request: AI prompt request
            user_id: Optional user ID to associate the interaction

        Returns:
            AI response
        """
        logger.info(f"Processing AI request for user: {user_id}")

        # Generate response using LLM service
        response = await self.llm_service.generate_response(request)

        # Business logic: Optionally save the interaction as a document
        if user_id:
            try:
                document_data = DocumentCreate(
                    title=f"AI Interaction: {request.prompt[:50]}...",
                    content=f"Prompt: {request.prompt}\n\nResponse: {response.response}",
                    meta_data={
                        "type": "ai_interaction",
                        "model": request.model,
                        "tokens_used": response.tokens_used,
                    },
                )
                self.document_repository.create(user_id, document_data)
                logger.info(f"Saved AI interaction for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to save AI interaction: {e}")
                # Don't fail the request if saving fails

        return response

    def get_user_documents(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Retrieve all documents for a user.

        Args:
            user_id: User's primary key
            skip: Pagination offset
            limit: Maximum results

        Returns:
            List of Document schemas
        """
        documents = self.document_repository.get_by_user(user_id, skip, limit)
        return [Document.model_validate(doc) for doc in documents]

    def get_document(self, document_id: int) -> Optional[Document]:
        """
        Retrieve a specific document.

        Args:
            document_id: Document's primary key

        Returns:
            Document schema if found, None otherwise
        """
        document = self.document_repository.get_by_id(document_id)
        return Document.model_validate(document) if document else None

    def create_document(self, user_id: int, document_data: DocumentCreate) -> Document:
        """
        Create a new document.

        Args:
            user_id: Owner's user ID
            document_data: Document creation data

        Returns:
            Created Document schema
        """
        document = self.document_repository.create(user_id, document_data)
        logger.info(f"Created document '{document.title}' for user {user_id}")
        return Document.model_validate(document)

    def update_document(
        self, document_id: int, document_data: DocumentUpdate
    ) -> Optional[Document]:
        """
        Update a document.

        Args:
            document_id: Document's primary key
            document_data: Updated document data

        Returns:
            Updated Document schema if found, None otherwise
        """
        document = self.document_repository.update(document_id, document_data)

        if document:
            logger.info(f"Updated document {document_id}")
            return Document.model_validate(document)

        return None

    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document.

        Args:
            document_id: Document's primary key

        Returns:
            True if deleted, False if not found
        """
        success = self.document_repository.delete(document_id)

        if success:
            logger.info(f"Deleted document {document_id}")

        return success

    def count_user_documents(self, user_id: int) -> int:
        """
        Count documents for a user.

        Args:
            user_id: User's primary key

        Returns:
            Document count
        """
        return self.document_repository.count_by_user(user_id)
