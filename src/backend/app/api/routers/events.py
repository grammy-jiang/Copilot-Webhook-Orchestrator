"""Events router for webhook event retrieval."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.api.schemas import EventListResponse, EventResponse
from app.db.engine import get_session
from app.db.models.user import User
from app.services.github import GitHubService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
async def list_events(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
    event_type: Annotated[str | None, Query(description="Filter by event type")] = None,
    repository_id: Annotated[
        int | None, Query(description="Filter by repository ID")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results")] = 50,
    offset: Annotated[int, Query(ge=0, description="Results offset")] = 0,
) -> EventListResponse:
    """List events for the current user.

    Args:
        current_user: The authenticated user.
        db: The database session.
        event_type: Optional event type filter.
        repository_id: Optional repository ID filter.
        limit: Maximum number of events to return.
        offset: Number of events to skip.

    Returns:
        Paginated list of events.
    """
    github_service = GitHubService(db)

    events = github_service.get_events_by_user(
        user_id=current_user.id,
        event_type=event_type,
        repository_id=repository_id,
        limit=limit,
        offset=offset,
    )

    total = github_service.count_events_by_user(
        user_id=current_user.id,
        event_type=event_type,
        repository_id=repository_id,
    )

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


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> EventResponse:
    """Get a specific event by ID.

    Args:
        event_id: The event ID.
        current_user: The authenticated user.
        db: The database session.

    Returns:
        The event details.

    Raises:
        HTTPException: If event not found or access denied.
    """
    github_service = GitHubService(db)

    # Get event from user's events
    events = github_service.get_events_by_user(
        user_id=current_user.id,
        limit=1000,  # Reasonable limit for search
        offset=0,
    )

    event = next((e for e in events if e.id == event_id), None)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventResponse(
        id=event.id,
        delivery_id=event.delivery_id,
        event_type=event.event_type,
        action=event.action,
        repository_id=event.repository_id,
        processed=event.processed,
        created_at=event.created_at,
    )
