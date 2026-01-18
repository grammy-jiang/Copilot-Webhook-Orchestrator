"""Webhook router for GitHub webhook handling."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlmodel import Session

from app.api.schemas import WebhookErrorResponse, WebhookResponse
from app.config import Settings, get_settings
from app.db.engine import get_session
from app.services.crypto import verify_webhook_signature
from app.services.github import GitHubService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/github",
    response_model=WebhookResponse,
    responses={
        400: {"model": WebhookErrorResponse},
        401: {"model": WebhookErrorResponse},
    },
)
async def handle_github_webhook(
    request: Request,
    db: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    x_github_event: Annotated[str, Header(description="GitHub event type")],
    x_github_delivery: Annotated[str, Header(description="GitHub delivery ID")],
    x_hub_signature_256: Annotated[
        str, Header(description="HMAC-SHA256 signature")
    ] = "",
) -> WebhookResponse:
    """Handle incoming GitHub webhooks.

    Validates the webhook signature, checks for duplicate delivery IDs,
    and stores the event for processing.

    Args:
        request: The incoming request.
        db: The database session.
        settings: Application settings.
        x_github_event: The GitHub event type header.
        x_github_delivery: The GitHub delivery ID header.
        x_hub_signature_256: The HMAC-SHA256 signature header.

    Returns:
        Webhook processing status.

    Raises:
        HTTPException: If signature is invalid or request is malformed.
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify signature
    if settings.github_webhook_secret:
        if not x_hub_signature_256:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature",
            )

        if not verify_webhook_signature(
            body, x_hub_signature_256, settings.github_webhook_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {e}",
        ) from e

    # Check for duplicate delivery (idempotency)
    github_service = GitHubService(db)
    if github_service.event_exists(x_github_delivery):
        return WebhookResponse(
            status="duplicate",
            delivery_id=x_github_delivery,
            event_type=x_github_event,
        )

    # Extract action if present
    action = payload.get("action")

    # Extract installation ID if present
    installation_id = None
    installation_data = payload.get("installation")
    if installation_data:
        github_installation_id = installation_data.get("id")
        if github_installation_id:
            installation = github_service.get_installation_by_github_id(
                github_installation_id
            )
            if installation:
                installation_id = installation.id

    # Extract repository ID if present
    repository_id = None
    repo_data = payload.get("repository")
    if repo_data:
        github_repo_id = repo_data.get("id")
        if github_repo_id:
            repo = github_service.get_repository_by_github_id(github_repo_id)
            if repo:
                repository_id = repo.id

    # Store the event
    github_service.create_event(
        delivery_id=x_github_delivery,
        event_type=x_github_event,
        payload=payload,
        action=action,
        repository_id=repository_id,
        installation_id=installation_id,
    )

    # Handle specific event types
    if x_github_event == "installation":
        await _handle_installation_event(payload, github_service)
    elif x_github_event == "installation_repositories":
        await _handle_installation_repositories_event(payload, github_service)

    return WebhookResponse(
        status="accepted",
        delivery_id=x_github_delivery,
        event_type=x_github_event,
    )


async def _handle_installation_event(
    payload: dict, github_service: GitHubService
) -> None:
    """Handle installation webhook events.

    Args:
        payload: The webhook payload.
        github_service: The GitHub service.
    """
    action = payload.get("action")
    installation = payload.get("installation", {})
    github_installation_id = installation.get("id")

    if not github_installation_id:
        return

    if action == "suspend":
        sender = payload.get("sender", {}).get("login", "unknown")
        github_service.suspend_installation(github_installation_id, sender)
    elif action == "unsuspend":
        github_service.unsuspend_installation(github_installation_id)
    elif action == "deleted":
        github_service.delete_installation(github_installation_id)


async def _handle_installation_repositories_event(
    payload: dict, github_service: GitHubService
) -> None:
    """Handle installation_repositories webhook events.

    Args:
        payload: The webhook payload.
        github_service: The GitHub service.
    """
    action = payload.get("action")
    installation_data = payload.get("installation", {})
    github_installation_id = installation_data.get("id")

    if not github_installation_id:
        return

    installation = github_service.get_installation_by_github_id(github_installation_id)
    if not installation:
        return

    if action == "added":
        repos_added = payload.get("repositories_added", [])
        for repo_data in repos_added:
            github_service.create_or_update_repository(
                installation=installation,
                github_repo_id=repo_data["id"],
                full_name=repo_data["full_name"],
                owner=repo_data["full_name"].split("/")[0],
                name=repo_data["name"],
                private=repo_data.get("private", False),
            )
