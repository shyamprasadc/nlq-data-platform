"""
AI/LLM Pydantic schemas for request/response validation.
Handles AI prompt requests and document operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AIPromptRequest(BaseModel):
    """
    Schema for AI prompt requests.

    Attributes:
        prompt: The user's prompt/question for the AI
        max_tokens: Maximum tokens in the response
        temperature: Sampling temperature (0.0 to 1.0)
        model: Optional model selection
    """

    prompt: str = Field(
        ..., min_length=1, max_length=4000, description="The prompt to send to the AI"
    )
    max_tokens: Optional[int] = Field(
        500, ge=1, le=2000, description="Maximum response length"
    )
    temperature: Optional[float] = Field(
        0.7, ge=0.0, le=1.0, description="Sampling temperature"
    )
    model: Optional[str] = Field("gpt-3.5-turbo", description="AI model to use")


class AIResponse(BaseModel):
    """
    Schema for AI response.

    Attributes:
        response: The AI-generated response text
        model: Model used for generation
        tokens_used: Number of tokens consumed
        metadata: Additional response metadata
    """

    response: str
    model: str
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentBase(BaseModel):
    """
    Base document schema.
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class DocumentCreate(DocumentBase):
    """
    Schema for creating a new document.
    """

    meta_data: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """
    Schema for updating a document.
    All fields are optional for partial updates.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    meta_data: Optional[Dict[str, Any]] = None


class Document(DocumentBase):
    """
    Schema for document responses.
    """

    id: int
    user_id: int
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    """
    Schema for paginated document list responses.
    """

    documents: list[Document]
    total: int
    page: int
    page_size: int
