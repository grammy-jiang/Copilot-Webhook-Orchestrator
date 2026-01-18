"""Repositories router for repository management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.api.schemas import (
    EventListResponse,
    EventResponse,
    RepositoryResponse,
)
from app.config import get_settings
from app.db.engine import get_session
from app.db.models.user import User
from app.services.github import GitHubService
from app.services.github_api import GitHubAPIClient, GitHubAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> RepositoryResponse:
    """Get a single repository by its GitHub ID.

    Fetches repository details from GitHub API.

    Args:
        repository_id: The GitHub repository ID.
        current_user: The authenticated user.
        db: The database session.

    Returns:
        Repository details.

    Raises:
        HTTPException: If repository not found or access denied.
    """
    github_service = GitHubService(db)
    installation = github_service.get_user_installation(current_user.id)

    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No installation found",
        )

    settings = get_settings()
    api_client = GitHubAPIClient(settings)

    try:
        # Get all repositories and find the one with matching ID
        result = await api_client.list_installation_repositories(
            installation_id=installation.github_installation_id,
            page=1,
            per_page=100,
        )
    except GitHubAPIError as e:
        logger.error("GitHub API error: %s", e)
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e

    repositories = result.get("repositories", [])

    # Find the repository with matching ID
    for repo in repositories:
        if repo.get("id") == repository_id:
            return RepositoryResponse(
                id=repo.get("id"),
                github_repo_id=repo.get("id"),
                installation_id=installation.id,
                full_name=repo.get("full_name", ""),
                owner=repo.get("owner", {}).get("login", ""),
                name=repo.get("name", ""),
                private=repo.get("private", False),
                default_branch=repo.get("default_branch", "main"),
                created_at=repo.get("created_at"),
                updated_at=repo.get("pushed_at") or repo.get("updated_at"),
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Repository not found",
    )


@router.get("/{repository_id}/events", response_model=EventListResponse)
async def get_repository_events(
    repository_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100, description="Max events")] = 20,
    offset: Annotated[int, Query(ge=0, description="Offset")] = 0,
) -> EventListResponse:
    """Get events for a specific repository.

    Args:
        repository_id: The GitHub repository ID.
        current_user: The authenticated user.
        db: The database session.
        limit: Maximum number of events to return.
        offset: Number of events to skip.

    Returns:
        List of events for the repository.
    """
    github_service = GitHubService(db)

    # Get the repository from the local database to get its internal ID
    repo = github_service.get_repository_by_github_id(repository_id)

    if repo:
        # Get events for this repository
        events = github_service.get_events_by_user(
            user_id=current_user.id,
            repository_id=repo.id,
            limit=limit,
            offset=offset,
        )
        total = github_service.count_events_by_user(
            user_id=current_user.id,
            repository_id=repo.id,
        )
    else:
        # No local repository record, return empty
        events = []
        total = 0

    return EventListResponse(
        events=[
            EventResponse(
                id=event.id,
                delivery_id=event.delivery_id,
                event_type=event.event_type,
                action=event.action,
                repository_id=event.repository_id,
                processed=event.processed,
                created_at=event.created_at,
            )
            for event in events
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
