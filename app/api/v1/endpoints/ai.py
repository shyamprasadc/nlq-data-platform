"""
AI/LLM endpoints.
Handles AI prompt requests and document management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.ai import (
    AIPromptRequest,
    AIResponse,
    Document,
    DocumentCreate,
    DocumentUpdate,
)
from app.services.ai_service import AIService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate", response_model=AIResponse, status_code=status.HTTP_200_OK)
async def generate_ai_response(
    request: AIPromptRequest,
    user_id: int = Query(None, description="Optional user ID to save interaction"),
    db: Session = Depends(get_db),
) -> AIResponse:
    """
    Generate an AI response from a prompt.

    This endpoint demonstrates AI/LLM integration readiness.
    Currently returns mock responses - replace with actual LLM calls in production.

    Args:
        request: AI prompt request with configuration
        user_id: Optional user ID to associate and save the interaction
        db: Database session (injected)

    Returns:
        AI-generated response

    Example:
        ```json
        {
            "prompt": "Explain FastAPI in simple terms",
            "max_tokens": 500,
            "temperature": 0.7,
            "model": "gpt-3.5-turbo"
        }
        ```
    """
    ai_service = AIService(db)

    try:
        response = await ai_service.generate_ai_response(request, user_id)
        return response
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI response",
        )


@router.get("/documents", response_model=List[Document], status_code=status.HTTP_200_OK)
def get_user_documents(
    user_id: int = Query(..., description="User ID to retrieve documents for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> List[Document]:
    """
    Retrieve all documents for a user.

    Supports pagination for large document collections.

    Args:
        user_id: User's primary key
        skip: Pagination offset
        limit: Maximum results
        db: Database session (injected)

    Returns:
        List of documents
    """
    ai_service = AIService(db)
    documents = ai_service.get_user_documents(user_id, skip, limit)
    return documents


@router.get(
    "/documents/{document_id}", response_model=Document, status_code=status.HTTP_200_OK
)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    """
    Retrieve a specific document.

    Args:
        document_id: Document's primary key
        db: Database session (injected)

    Returns:
        Document data

    Raises:
        HTTPException: If document not found
    """
    ai_service = AIService(db)
    document = ai_service.get_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    return document


@router.post("/documents", response_model=Document, status_code=status.HTTP_201_CREATED)
def create_document(
    user_id: int = Query(..., description="Owner's user ID"),
    document_data: DocumentCreate = ...,
    db: Session = Depends(get_db),
) -> Document:
    """
    Create a new document.

    Args:
        user_id: Owner's user ID
        document_data: Document creation data
        db: Database session (injected)

    Returns:
        Created document
    """
    ai_service = AIService(db)
    document = ai_service.create_document(user_id, document_data)
    return document


@router.put(
    "/documents/{document_id}", response_model=Document, status_code=status.HTTP_200_OK
)
def update_document(
    document_id: int, document_data: DocumentUpdate, db: Session = Depends(get_db)
) -> Document:
    """
    Update a document.

    Args:
        document_id: Document's primary key
        document_data: Updated document data
        db: Database session (injected)

    Returns:
        Updated document

    Raises:
        HTTPException: If document not found
    """
    ai_service = AIService(db)
    document = ai_service.update_document(document_id, document_data)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a document.

    Args:
        document_id: Document's primary key
        db: Database session (injected)

    Raises:
        HTTPException: If document not found
    """
    ai_service = AIService(db)
    success = ai_service.delete_document(document_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
