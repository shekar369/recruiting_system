"""
Authentication dependencies for protected routes
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.jwt import verify_token
from app.services.auth_service import AuthService

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user

    Args:
        current_user: Current user from token

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_role(required_role: UserRole):
    """
    Dependency factory to require specific role

    Args:
        required_role: Required user role

    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # Define role hierarchy
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.HIRING_MANAGER: 1,
            UserRole.RECRUITER: 2,
            UserRole.ADMIN: 3
        }

        current_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        # Superusers bypass role checks
        if current_user.is_superuser:
            return current_user

        if current_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}"
            )

        return current_user

    return role_checker


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require admin role

    Args:
        current_user: Current user

    Returns:
        User if admin

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_superuser and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_recruiter_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require recruiter role or higher

    Args:
        current_user: Current user

    Returns:
        User if recruiter or admin

    Raises:
        HTTPException: If user is not recruiter or admin
    """
    allowed_roles = [UserRole.RECRUITER, UserRole.ADMIN]
    if not current_user.is_superuser and current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter privileges required"
        )
    return current_user


async def get_hiring_manager_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require hiring manager role or higher

    Args:
        current_user: Current user

    Returns:
        User if hiring manager, recruiter, or admin

    Raises:
        HTTPException: If user doesn't have sufficient privileges
    """
    allowed_roles = [UserRole.HIRING_MANAGER, UserRole.RECRUITER, UserRole.ADMIN]
    if not current_user.is_superuser and current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hiring manager privileges required"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")

        if payload is None:
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = await AuthService.get_user_by_id(db, user_id)
        return user
    except Exception:
        return None
