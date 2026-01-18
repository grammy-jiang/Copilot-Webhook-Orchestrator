"""GitHub API client for installation-level operations."""

import httpx

from app.config import Settings
from app.services.crypto import generate_github_app_jwt


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
        """
        super().__init__(message)
        self.status_code = status_code


class GitHubAPIClient:
    """Async client for GitHub API using installation access tokens."""

    BASE_URL = "https://api.github.com"

    def __init__(self, settings: Settings) -> None:
        """Initialize the GitHub API client.

        Args:
            settings: Application settings with GitHub App credentials.
        """
        self.settings = settings
        self._installation_tokens: dict[int, str] = {}

    def _get_app_jwt(self) -> str:
        """Generate a GitHub App JWT for authentication.

        Returns:
            The encoded JWT string.

        Raises:
            GitHubAPIError: If App credentials are not configured.
        """
        if not self.settings.github_app_id or not self.settings.github_private_key:
            raise GitHubAPIError(
                "GitHub App credentials not configured", status_code=500
            )

        return generate_github_app_jwt(
            self.settings.github_app_id,
            self.settings.github_private_key,
        )

    async def get_installation_access_token(
        self, installation_id: int
    ) -> str:
        """Get an installation access token from GitHub.

        Args:
            installation_id: The GitHub installation ID.

        Returns:
            The installation access token.

        Raises:
            GitHubAPIError: If token request fails.
        """
        app_jwt = self._get_app_jwt()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {app_jwt}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 201:
                raise GitHubAPIError(
                    f"Failed to get installation token: {response.text}",
                    status_code=response.status_code,
                )

            data = response.json()
            return data["token"]

    async def list_installation_repositories(
        self,
        installation_id: int,
        page: int = 1,
        per_page: int = 30,
    ) -> dict:
        """List repositories accessible to an installation.

        Args:
            installation_id: The GitHub installation ID.
            page: Page number (1-indexed).
            per_page: Number of items per page (max 100).

        Returns:
            Dict with 'total_count' and 'repositories' keys.

        Raises:
            GitHubAPIError: If API request fails.
        """
        token = await self.get_installation_access_token(installation_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/installation/repositories",
                params={"page": page, "per_page": min(per_page, 100)},
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 200:
                raise GitHubAPIError(
                    f"Failed to list repositories: {response.text}",
                    status_code=response.status_code,
                )

            return response.json()

    async def get_installation(self, installation_id: int) -> dict:
        """Get installation details from GitHub.

        Args:
            installation_id: The GitHub installation ID.

        Returns:
            Installation data from GitHub API.

        Raises:
            GitHubAPIError: If API request fails.
        """
        app_jwt = self._get_app_jwt()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/app/installations/{installation_id}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {app_jwt}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 200:
                raise GitHubAPIError(
                    f"Failed to get installation: {response.text}",
                    status_code=response.status_code,
                )

            return response.json()
