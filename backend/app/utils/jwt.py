"""
JWT token utilities for authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token

    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta (default 7 days)

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        InvalidTokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except InvalidTokenError:
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify JWT token and return payload

    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Verify token type
        if payload.get("type") != token_type:
            return None

        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None

        if datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        return payload
    except InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> Optional[UUID]:
    """
    Extract user ID from token

    Args:
        token: JWT token

    Returns:
        User ID if valid, None otherwise
    """
    payload = verify_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        return UUID(user_id)
    except (ValueError, AttributeError):
        return None
