"""GitHub service for API interactions and webhook handling."""

import json
from datetime import UTC, datetime

from sqlalchemy import desc
from sqlmodel import Session, select

from app.db.models.event import Event
from app.db.models.installation import Installation
from app.db.models.repository import Repository
from app.db.models.user import User


class GitHubService:
    """Service for GitHub API and webhook operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the GitHub service.

        Args:
            db: The database session.
        """
        self.db = db

    # Installation methods

    def get_installation_by_github_id(
        self, github_installation_id: int
    ) -> Installation | None:
        """Get an installation by its GitHub installation ID.

        Args:
            github_installation_id: The GitHub installation ID.

        Returns:
            The installation if found, None otherwise.
        """
        statement = select(Installation).where(
            Installation.github_installation_id == github_installation_id
        )
        return self.db.exec(statement).first()

    def get_user_installation(self, user_id: int) -> Installation | None:
        """Get the installation for a user.

        Args:
            user_id: The user ID.

        Returns:
            The user's active installation if found, None otherwise.
        """
        statement = select(Installation).where(
            Installation.user_id == user_id,
            Installation.status == "active",
        )
        return self.db.exec(statement).first()

    def create_installation(
        self,
        user: User,
        github_installation_id: int,
        account_type: str,
        account_login: str,
        account_id: int,
        target_type: str = "all",
        permissions: dict | None = None,
        events: list[str] | None = None,
    ) -> Installation:
        """Create a new GitHub App installation.

        Args:
            user: The user who installed the app.
            github_installation_id: The GitHub installation ID.
            account_type: The account type (User or Organization).
            account_login: The account login name.
            account_id: The GitHub account ID.
            target_type: Repository selection type.
            permissions: Granted permissions.
            events: Subscribed events.

        Returns:
            The created installation.
        """
        installation = Installation(
            github_installation_id=github_installation_id,
            user_id=user.id,
            account_type=account_type,
            account_login=account_login,
            account_id=account_id,
            target_type=target_type,
            permissions=json.dumps(permissions or {}),
            events=json.dumps(events or []),
            status="active",
        )
        self.db.add(installation)
        self.db.commit()
        self.db.refresh(installation)
        return installation

    def suspend_installation(
        self, github_installation_id: int, suspended_by: str
    ) -> Installation | None:
        """Suspend an installation.

        Args:
            github_installation_id: The GitHub installation ID.
            suspended_by: Who suspended the installation.

        Returns:
            The updated installation if found, None otherwise.
        """
        installation = self.get_installation_by_github_id(github_installation_id)
        if not installation:
            return None

        installation.status = "suspended"
        installation.suspended_at = datetime.now(UTC)
        installation.suspended_by = suspended_by
        installation.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(installation)
        return installation

    def unsuspend_installation(
        self, github_installation_id: int
    ) -> Installation | None:
        """Unsuspend an installation.

        Args:
            github_installation_id: The GitHub installation ID.

        Returns:
            The updated installation if found, None otherwise.
        """
        installation = self.get_installation_by_github_id(github_installation_id)
        if not installation:
            return None

        installation.status = "active"
        installation.suspended_at = None
        installation.suspended_by = None
        installation.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(installation)
        return installation

    def delete_installation(self, github_installation_id: int) -> bool:
        """Mark an installation as deleted.

        Args:
            github_installation_id: The GitHub installation ID.

        Returns:
            True if installation was found and deleted, False otherwise.
        """
        installation = self.get_installation_by_github_id(github_installation_id)
        if not installation:
            return False

        installation.status = "deleted"
        installation.updated_at = datetime.now(UTC)
        self.db.commit()
        return True

    # Repository methods

    def get_repositories_for_user(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 12,
        search: str | None = None,
    ) -> tuple[list[Repository], int]:
        """Get repositories accessible to a user via their installation.

        Args:
            user_id: The user ID.
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Optional search filter for repository name.

        Returns:
            Tuple of (list of repositories, total count).
        """
        # Get user's installation
        installation = self.get_user_installation(user_id)
        if not installation:
            return [], 0

        # Build query
        statement = select(Repository).where(
            Repository.installation_id == installation.id
        )

        # Apply search filter if provided
        if search:
            statement = statement.where(Repository.full_name.ilike(f"%{search}%"))

        # Get total count
        count_statement = select(Repository).where(
            Repository.installation_id == installation.id
        )
        if search:
            count_statement = count_statement.where(
                Repository.full_name.ilike(f"%{search}%")
            )
        total = len(list(self.db.exec(count_statement)))

        # Apply pagination
        offset = (page - 1) * per_page
        statement = statement.offset(offset).limit(per_page)

        repositories = list(self.db.exec(statement))
        return repositories, total

    def get_repository_by_github_id(self, github_repo_id: int) -> Repository | None:
        """Get a repository by its GitHub ID.

        Args:
            github_repo_id: The GitHub repository ID.

        Returns:
            The repository if found, None otherwise.
        """
        statement = select(Repository).where(
            Repository.github_repo_id == github_repo_id
        )
        return self.db.exec(statement).first()

    def create_or_update_repository(
        self,
        installation: Installation,
        github_repo_id: int,
        full_name: str,
        owner: str,
        name: str,
        private: bool = False,
        default_branch: str = "main",
    ) -> Repository:
        """Create or update a repository record.

        Args:
            installation: The installation that has access.
            github_repo_id: The GitHub repository ID.
            full_name: The full repository name (owner/repo).
            owner: The repository owner.
            name: The repository name.
            private: Whether the repo is private.
            default_branch: The default branch name.

        Returns:
            The created or updated repository.
        """
        repo = self.get_repository_by_github_id(github_repo_id)

        if repo:
            repo.installation_id = installation.id
            repo.full_name = full_name
            repo.owner = owner
            repo.name = name
            repo.private = private
            repo.default_branch = default_branch
            repo.updated_at = datetime.now(UTC)
        else:
            repo = Repository(
                github_repo_id=github_repo_id,
                installation_id=installation.id,
                full_name=full_name,
                owner=owner,
                name=name,
                private=private,
                default_branch=default_branch,
            )
            self.db.add(repo)

        self.db.commit()
        self.db.refresh(repo)
        return repo

    # Event methods

    def event_exists(self, delivery_id: str) -> bool:
        """Check if an event with the given delivery ID exists.

        Args:
            delivery_id: The GitHub delivery ID.

        Returns:
            True if event exists, False otherwise.
        """
        statement = select(Event).where(Event.delivery_id == delivery_id)
        return self.db.exec(statement).first() is not None

    def create_event(
        self,
        delivery_id: str,
        event_type: str,
        payload: dict,
        action: str | None = None,
        repository_id: int | None = None,
        installation_id: int | None = None,
        user_id: int | None = None,
    ) -> Event:
        """Create a new webhook event record.

        Args:
            delivery_id: The GitHub delivery ID.
            event_type: The event type.
            payload: The webhook payload.
            action: The event action.
            repository_id: The repository ID.
            installation_id: The installation ID.
            user_id: The user ID.

        Returns:
            The created event.
        """
        event = Event(
            delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            repository_id=repository_id,
            installation_id=installation_id,
            user_id=user_id,
            payload=json.dumps(payload),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_event_by_delivery_id(self, delivery_id: str) -> Event | None:
        """Get an event by its delivery ID.

        Args:
            delivery_id: The GitHub delivery ID.

        Returns:
            The event if found, None otherwise.
        """
        statement = select(Event).where(Event.delivery_id == delivery_id)
        return self.db.exec(statement).first()

    def get_events_by_user(
        self,
        user_id: int,
        event_type: str | None = None,
        repository_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]:
        """Get events for a user with optional filtering.

        Args:
            user_id: The user ID.
            event_type: Optional event type filter.
            repository_id: Optional repository ID filter.
            limit: Maximum number of events to return.
            offset: Number of events to skip.

        Returns:
            List of matching events.
        """
        statement = select(Event).where(Event.user_id == user_id)

        if event_type:
            statement = statement.where(Event.event_type == event_type)

        if repository_id:
            statement = statement.where(Event.repository_id == repository_id)

        statement = statement.order_by(desc(Event.created_at))
        statement = statement.offset(offset).limit(limit)

        return list(self.db.exec(statement).all())

    def count_events_by_user(
        self,
        user_id: int,
        event_type: str | None = None,
        repository_id: int | None = None,
    ) -> int:
        """Count events for a user with optional filtering.

        Args:
            user_id: The user ID.
            event_type: Optional event type filter.
            repository_id: Optional repository ID filter.

        Returns:
            Number of matching events.
        """
        statement = select(Event).where(Event.user_id == user_id)

        if event_type:
            statement = statement.where(Event.event_type == event_type)

        if repository_id:
            statement = statement.where(Event.repository_id == repository_id)

        return len(self.db.exec(statement).all())

    def mark_event_processed(
        self, event_id: int, error: str | None = None
    ) -> Event | None:
        """Mark an event as processed.

        Args:
            event_id: The event ID.
            error: Optional error message if processing failed.

        Returns:
            The updated event if found, None otherwise.
        """
        statement = select(Event).where(Event.id == event_id)
        event = self.db.exec(statement).first()

        if not event:
            return None

        event.processed = True
        event.processed_at = datetime.now(UTC)
        event.error = error
        event.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_last_event_at_for_repositories(
        self, repository_github_ids: list[int]
    ) -> dict[int, datetime | None]:
        """Get the last event timestamp for multiple repositories.

        Args:
            repository_github_ids: List of GitHub repository IDs.

        Returns:
            Dictionary mapping GitHub repo ID to last event timestamp.
        """
        result: dict[int, datetime | None] = dict.fromkeys(repository_github_ids)

        if not repository_github_ids:
            return result

        # Get all repositories by GitHub IDs
        repos_statement = select(Repository).where(
            Repository.github_repo_id.in_(repository_github_ids)
        )
        repos = list(self.db.exec(repos_statement))

        # Map internal ID to GitHub ID
        internal_to_github: dict[int, int] = {}
        for repo in repos:
            if repo.id is not None:
                internal_to_github[repo.id] = repo.github_repo_id

        if not internal_to_github:
            return result

        # Get the most recent event for each repository
        for internal_id, github_id in internal_to_github.items():
            event_statement = (
                select(Event)
                .where(Event.repository_id == internal_id)
                .order_by(desc(Event.created_at))
                .limit(1)
            )
            event = self.db.exec(event_statement).first()
            if event:
                result[github_id] = event.created_at

        return result
