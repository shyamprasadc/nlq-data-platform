"""
User Pydantic schemas for request/response validation.
Separates API layer from database models.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    Used as a foundation for other user schemas.
    """

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    """
    Schema for user registration/creation.
    Includes password field for initial account setup.
    """

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    All fields are optional to support partial updates.
    """

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """
    Schema representing a user as stored in the database.
    Includes internal fields like id and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class User(UserBase):
    """
    Schema for user responses in API endpoints.
    Excludes sensitive information like hashed_password.
    """

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """
    Schema for user login requests.
    """

    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Schema for JWT token response.
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for data encoded in JWT tokens.
    """

    user_id: Optional[int] = None
    email: Optional[str] = None
