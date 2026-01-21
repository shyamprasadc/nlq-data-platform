"""
User repository for database operations.
Implements the repository pattern to isolate database logic from business logic.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate
from backend.core.security import get_password_hash


class UserRepository:
    """
    Repository for User model database operations.

    This class encapsulates all database queries related to users.
    Benefits:
    - Separates data access from business logic
    - Makes testing easier (can mock repository)
    - Centralizes query logic
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: User's primary key

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User objects
        """
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data with plain password

        Returns:
            Created User object
        """
        # Hash the password before storing
        hashed_password = get_password_hash(user_data.password)

        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.

        Args:
            user_id: User's primary key
            user_data: Updated user data

        Returns:
            Updated User object if found, None otherwise
        """
        db_user = self.get_by_id(user_id)

        if not db_user:
            return None

        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)

        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def delete(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: User's primary key

        Returns:
            True if deleted, False if not found
        """
        db_user = self.get_by_id(user_id)

        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()

        return True

    def count(self) -> int:
        """
        Count total number of users.

        Returns:
            Total user count
        """
        return self.db.query(User).count()
