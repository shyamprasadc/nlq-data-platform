"""
User service containing business logic for user operations.
Acts as an intermediary between API routes and repositories.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import verify_password
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """
    Service layer for user-related business logic.

    This layer:
    - Contains business rules and validation
    - Coordinates between repositories
    - Handles complex operations that span multiple repositories
    - Keeps routes thin and focused on HTTP concerns
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.repository = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: User's primary key

        Returns:
            User schema if found, None otherwise
        """
        user = self.repository.get_by_id(user_id)
        return User.model_validate(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email: User's email address

        Returns:
            User schema if found, None otherwise
        """
        user = self.repository.get_by_email(email)
        return User.model_validate(user) if user else None

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with business logic validation.

        Args:
            user_data: User creation data

        Returns:
            Created User schema

        Raises:
            ValueError: If email already exists
        """
        # Business logic: Check if email already exists
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            logger.warning(
                f"Attempted to create user with existing email: {user_data.email}"
            )
            raise ValueError("Email already registered")

        # Additional business logic could go here:
        # - Email validation
        # - Password strength requirements
        # - User verification workflow

        user = self.repository.create(user_data)
        logger.info(f"Created new user: {user.email}")

        return User.model_validate(user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User's primary key
            user_data: Updated user data

        Returns:
            Updated User schema if found, None otherwise

        Raises:
            ValueError: If email already exists for another user
        """
        # Business logic: If updating email, check it's not taken
        if user_data.email:
            existing_user = self.repository.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already in use")

        user = self.repository.update(user_id, user_data)

        if user:
            logger.info(f"Updated user: {user.email}")
            return User.model_validate(user)

        return None

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: User's primary key

        Returns:
            True if deleted, False if not found
        """
        success = self.repository.delete(user_id)

        if success:
            logger.info(f"Deleted user with ID: {user_id}")

        return success

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            User schema if authentication successful, None otherwise
        """
        user = self.repository.get_by_email(email)

        if not user:
            logger.warning(f"Authentication failed: User not found for email {email}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: Inactive user {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for {email}")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return User.model_validate(user)
