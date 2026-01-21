"""
User management endpoints.
Handles user CRUD operations - thin controllers that delegate to service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.user import User, UserCreate, UserUpdate
from backend.services.user_service import UserService
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Create a new user.

    This endpoint is thin - it only handles HTTP concerns.
    All business logic is delegated to the service layer.

    Args:
        user_data: User creation data
        db: Database session (injected)

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists
    """
    user_service = UserService(db)

    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        # Service layer raised a business logic error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    """
    Retrieve a user by ID.

    Args:
        user_id: User's primary key
        db: Database session (injected)

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user


@router.put("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)
) -> User:
    """
    Update a user.

    Args:
        user_id: User's primary key
        user_data: Updated user data
        db: Database session (injected)

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or validation fails
    """
    user_service = UserService(db)

    try:
        user = user_service.update_user(user_id, user_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a user.

    Args:
        user_id: User's primary key
        db: Database session (injected)

    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    success = user_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
