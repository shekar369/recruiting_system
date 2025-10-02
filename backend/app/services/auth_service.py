"""
Authentication service for user management and authentication
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and user management"""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        stmt = select(User).where(User.username == user_data.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"Username '{user_data.username}' already exists")

        # Check if email exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"Email '{user_data.email}' already exists")

        # Create user
        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            role=user_data.role,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )

        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"User created: {user.username} ({user.email})")
            return user
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Error creating user: {e}")
            raise ValueError("User creation failed due to database constraint")

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password

        Args:
            db: Database session
            username: Username or email
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        # Try to find user by username or email
        stmt = select(User).where(
            (User.username == username) | (User.email == username)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: User inactive - {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        logger.info(f"User authenticated: {user.username}")
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Get user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            db: Database session
            username: Username

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            db: Database session
            email: Email address

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Update user

        Args:
            db: Database session
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user if found, None otherwise

        Raises:
            ValueError: If username or email already exists
        """
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            return None

        # Check username uniqueness if being updated
        if user_data.username and user_data.username != user.username:
            stmt = select(User).where(User.username == user_data.username)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise ValueError(f"Username '{user_data.username}' already exists")

        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            stmt = select(User).where(User.email == user_data.email)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise ValueError(f"Email '{user_data.email}' already exists")

        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        logger.info(f"User updated: {user.username}")
        return user

    @staticmethod
    async def change_password(db: AsyncSession, user_id: UUID, old_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            db: Database session
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise
        """
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            return False

        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed: Invalid old password - {user.username}")
            return False

        user.hashed_password = hash_password(new_password)
        await db.commit()
        logger.info(f"Password changed: {user.username}")
        return True

    @staticmethod
    def create_tokens(user: User) -> dict:
        """
        Create access and refresh tokens for user

        Args:
            user: User object

        Returns:
            Dictionary with access_token, refresh_token, and token_type
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """
        Delete user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        logger.info(f"User deleted: {user.username}")
        return True
