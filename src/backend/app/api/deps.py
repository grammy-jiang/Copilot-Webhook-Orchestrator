"""API dependencies for FastAPI."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session

from app.db.engine import get_session
from app.db.models.user import User
from app.services.auth import AuthService


def get_auth_service(
    db: Annotated[Session, Depends(get_session)],
) -> AuthService:
    """Get an AuthService instance.

    Args:
        db: The database session.

    Returns:
        An AuthService instance.
    """
    return AuthService(db)


def get_current_user(
    session_token: Annotated[str | None, Cookie(alias="session_token")] = None,
    auth_service: Annotated[AuthService | None, Depends(get_auth_service)] = None,
) -> User:
    """Get the current authenticated user.

    Args:
        session_token: The session token from cookie.
        auth_service: The auth service.

    Returns:
        The authenticated user.

    Raises:
        HTTPException: If not authenticated or session is invalid.
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_user_by_session_token(session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_user(
    session_token: Annotated[str | None, Cookie(alias="session_token")] = None,
    auth_service: Annotated[AuthService | None, Depends(get_auth_service)] = None,
) -> User | None:
    """Get the current user if authenticated, None otherwise.

    Args:
        session_token: The session token from cookie.
        auth_service: The auth service.

    Returns:
        The authenticated user or None.
    """
    if not session_token:
        return None

    return auth_service.get_user_by_session_token(session_token)
