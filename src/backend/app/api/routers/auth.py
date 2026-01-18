"""Authentication router for OAuth and session management."""

import logging
import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.api.deps import get_auth_service, get_current_user, get_optional_user
from app.api.schemas import UserResponse
from app.config import get_settings
from app.db.engine import get_session
from app.db.models.user import User
from app.services.auth import AuthService
from app.services.github import GitHubService
from app.services.github_api import GitHubAPIClient, GitHubAPIError

logger = logging.getLogger(__name__)

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
    db: Annotated[Session, Depends(get_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    existing_user: Annotated[User | None, Depends(get_optional_user)],
    code: Annotated[str | None, Query(description="GitHub OAuth authorization code")] = None,
    state: Annotated[str | None, Query(description="OAuth state parameter")] = None,
    installation_id: Annotated[
        int | None, Query(description="GitHub App installation ID")
    ] = None,
    setup_action: Annotated[
        str | None, Query(description="GitHub App setup action")
    ] = None,
) -> RedirectResponse:
    """Handle GitHub OAuth callback and GitHub App installation callback.

    This endpoint handles two different flows:
    1. OAuth login: Called with `code` and `state` parameters
    2. GitHub App installation: Called with `code`, `installation_id`, and `setup_action`

    For installation callbacks, if the user is already authenticated (has a valid session),
    we redirect directly to the repositories page without re-authenticating.

    Args:
        request: The incoming request.
        db: The database session.
        auth_service: The auth service.
        existing_user: The currently authenticated user, if any.
        code: The authorization code from GitHub.
        state: The state parameter for CSRF validation (OAuth login flow).
        installation_id: GitHub App installation ID (installation flow).
        setup_action: Setup action type (installation flow).

    Returns:
        Redirect to the frontend with session cookie set.
    """
    settings = get_settings()

    # Determine which flow this is
    is_installation_flow = installation_id is not None

    # For installation callbacks, if user already has a valid session, create installation and redirect
    if is_installation_flow and existing_user is not None:
        # Create or update the installation record
        await _create_or_update_installation(
            db=db,
            user=existing_user,
            installation_id=installation_id,
        )
        return RedirectResponse(
            url=f"{settings.frontend_url}/repositories",
            status_code=status.HTTP_302_FOUND,
        )

    # If no code provided (shouldn't happen, but handle gracefully)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization code provided",
        )
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

    # Determine redirect URL based on flow type
    if is_installation_flow:
        # For GitHub App installation, create installation record and redirect to repositories page
        await _create_or_update_installation(
            db=db,
            user=user,
            installation_id=installation_id,
        )
        redirect_url = f"{settings.frontend_url}/repositories"
    else:
        # For regular OAuth login, redirect to frontend home
        redirect_url = settings.frontend_url

    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
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


async def _create_or_update_installation(
    db: Session,
    user: User,
    installation_id: int,
) -> None:
    """Create or update an installation record from GitHub API.

    Fetches installation details from GitHub and creates/updates
    the local installation record.

    Args:
        db: The database session.
        user: The user who owns the installation.
        installation_id: The GitHub installation ID.
    """
    settings = get_settings()
    github_service = GitHubService(db)
    api_client = GitHubAPIClient(settings)

    # Check if installation already exists
    existing = github_service.get_installation_by_github_id(installation_id)
    if existing:
        # Installation already exists, no need to create
        logger.info("Installation %s already exists for user %s", installation_id, user.id)
        return

    try:
        # Fetch installation details from GitHub
        installation_data = await api_client.get_installation(installation_id)

        # Create the installation record
        github_service.create_installation(
            user=user,
            github_installation_id=installation_id,
            account_type=installation_data.get("account", {}).get("type", "User"),
            account_login=installation_data.get("account", {}).get("login", ""),
            account_id=installation_data.get("account", {}).get("id", 0),
            target_type=installation_data.get("repository_selection", "all"),
            permissions=installation_data.get("permissions", {}),
            events=installation_data.get("events", []),
        )
        logger.info(
            "Created installation %s for user %s",
            installation_id,
            user.id,
        )
    except GitHubAPIError as e:
        logger.error("Failed to fetch installation %s: %s", installation_id, e)
