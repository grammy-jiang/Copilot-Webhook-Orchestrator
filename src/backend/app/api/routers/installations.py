"""Installations router for GitHub App installation management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.api.deps import get_current_user
from app.api.schemas import InstallationListResponse, InstallationResponse
from app.config import get_settings
from app.db.engine import get_session
from app.db.models.user import User
from app.services.github import GitHubService

router = APIRouter(prefix="/installations", tags=["installations"])


@router.get("/connect")
async def connect_installation(
    current_user: Annotated[User | None, Depends(get_current_user)] = None,
) -> RedirectResponse:
    """Redirect to GitHub App installation page.

    Args:
        current_user: The authenticated user.

    Returns:
        Redirect to GitHub App installation page.

    Raises:
        HTTPException: If user is not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be authenticated to install the GitHub App",
        )

    settings = get_settings()
    github_app_url = (
        f"https://github.com/apps/{settings.github_app_slug}/installations/new"
    )

    return RedirectResponse(url=github_app_url, status_code=status.HTTP_302_FOUND)


@router.get("", response_model=InstallationListResponse)
async def list_installations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> InstallationListResponse:
    """List all installations for the current user.

    Args:
        current_user: The authenticated user.
        db: The database session.

    Returns:
        List of installations.
    """
    github_service = GitHubService(db)
    installation = github_service.get_user_installation(current_user.id)

    if installation:
        installations = [
            InstallationResponse(
                id=installation.id,
                github_installation_id=installation.github_installation_id,
                account_type=installation.account_type,
                account_login=installation.account_login,
                status=installation.status,
                created_at=installation.created_at,
            )
        ]
        return InstallationListResponse(installations=installations, total=1)

    return InstallationListResponse(installations=[], total=0)


@router.get("/callback")
async def installation_callback(
    installation_id: Annotated[int, Query(description="GitHub installation ID")],
    setup_action: Annotated[str, Query(description="Setup action type")] = "install",
    current_user: Annotated[User | None, Depends(get_current_user)] = None,
    db: Annotated[Session | None, Depends(get_session)] = None,
) -> dict:
    """Handle GitHub App installation callback.

    This endpoint is called after a user installs the GitHub App.

    Args:
        installation_id: The GitHub installation ID.
        setup_action: The setup action (install, update, etc.).
        current_user: The authenticated user.
        db: The database session.

    Returns:
        Installation status.

    Raises:
        HTTPException: If user is not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be authenticated to complete installation",
        )

    github_service = GitHubService(db)

    # Check if user already has an installation
    existing = github_service.get_user_installation(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active installation",
        )

    # Note: In production, we would fetch installation details from GitHub API
    # For now, we create a placeholder that will be updated by the webhook
    installation = github_service.create_installation(
        user=current_user,
        github_installation_id=installation_id,
        account_type="User",
        account_login=current_user.github_login,
        account_id=current_user.github_id,
    )

    return {
        "status": "success",
        "installation_id": installation.id,
        "github_installation_id": installation_id,
    }


@router.get("/{installation_id}", response_model=InstallationResponse)
async def get_installation(
    installation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> InstallationResponse:
    """Get a specific installation.

    Args:
        installation_id: The installation ID.
        current_user: The authenticated user.
        db: The database session.

    Returns:
        The installation details.

    Raises:
        HTTPException: If installation not found or access denied.
    """
    github_service = GitHubService(db)
    installation = github_service.get_user_installation(current_user.id)

    if not installation or installation.id != installation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation not found",
        )

    return InstallationResponse(
        id=installation.id,
        github_installation_id=installation.github_installation_id,
        account_type=installation.account_type,
        account_login=installation.account_login,
        status=installation.status,
        created_at=installation.created_at,
    )
