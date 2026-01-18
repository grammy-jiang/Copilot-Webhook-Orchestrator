"""Authentication router for OAuth and session management."""

import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.api.deps import get_auth_service, get_current_user
from app.api.schemas import UserResponse
from app.config import get_settings
from app.db.engine import get_session
from app.db.models.user import User
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    redirect_uri: str | None = None,
) -> RedirectResponse:
    """Initiate GitHub OAuth login flow.

    Args:
        request: The incoming request.
        auth_service: The auth service.
        redirect_uri: Optional URI to redirect to after login.

    Returns:
        Redirect to GitHub authorization page.
    """
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session (in production, use proper session storage)
    # For now, we'll encode it in the state parameter
    auth_url = auth_service.get_oauth_authorization_url(state)

    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: Annotated[str, Query(description="GitHub OAuth authorization code")],
    state: Annotated[str, Query(description="OAuth state parameter")],
    db: Annotated[Session, Depends(get_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RedirectResponse:
    """Handle GitHub OAuth callback.

    Args:
        request: The incoming request.
        code: The authorization code from GitHub.
        state: The state parameter for CSRF validation.
        db: The database session.
        auth_service: The auth service.

    Returns:
        Redirect to the frontend with session cookie set.
    """
    # Exchange code for access token
    access_token = await auth_service.exchange_code_for_token(code)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for access token",
        )

    # Get user info from GitHub
    github_user = await auth_service.get_github_user(access_token)
    if not github_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from GitHub",
        )

    # Create or update user
    user = auth_service.get_or_create_user(
        github_id=github_user["id"],
        github_login=github_user["login"],
        github_name=github_user.get("name"),
        github_email=github_user.get("email"),
        github_avatar_url=github_user.get("avatar_url"),
        access_token=access_token,
    )

    # Create session
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None
    session, token = auth_service.create_session(
        user=user,
        user_agent=user_agent,
        ip_address=client_ip,
    )

    # Redirect to frontend with session cookie
    settings = get_settings()
    response = RedirectResponse(
        url=settings.frontend_url, status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=session.expires_at.timestamp() - session.created_at.timestamp(),
    )

    return response


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get the current authenticated user's information.

    Args:
        current_user: The authenticated user.

    Returns:
        The user information.
    """
    return UserResponse(
        id=current_user.id,
        github_id=current_user.github_id,
        github_login=current_user.github_login,
        github_name=current_user.github_name,
        github_email=current_user.github_email,
        github_avatar_url=current_user.github_avatar_url,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
    )


@router.get("/logout")
async def logout(
    session_token: Annotated[str | None, Cookie(alias="session_token")] = None,
    auth_service: Annotated[AuthService | None, Depends(get_auth_service)] = None,
) -> RedirectResponse:
    """Log out the current user by invalidating their session.

    Args:
        session_token: The session token from cookie.
        auth_service: The auth service.

    Returns:
        Redirect to login page with session cookie cleared.
    """
    if session_token and auth_service:
        auth_service.invalidate_session(session_token)

    settings = get_settings()
    response = RedirectResponse(
        url=f"{settings.frontend_url}/login?logout=success",
        status_code=status.HTTP_302_FOUND,
    )
    # Delete cookie with same parameters as set_cookie for proper removal
    response.delete_cookie(
        key="session_token",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
    )
    return response
