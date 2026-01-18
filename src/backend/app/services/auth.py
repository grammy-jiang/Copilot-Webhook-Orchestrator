"""Authentication service for OAuth and session management."""

from datetime import UTC, datetime, timedelta

import httpx
from sqlmodel import Session, select

from app.config import get_settings
from app.db.models.session import Session as UserSession
from app.db.models.user import User
from app.services.crypto import generate_session_token, hash_token


class AuthService:
    """Service for handling authentication and session management."""

    GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"

    def __init__(self, db: Session) -> None:
        """Initialize the auth service.

        Args:
            db: The database session.
        """
        self.db = db
        self.settings = get_settings()

    def get_oauth_authorization_url(self, state: str) -> str:
        """Generate the GitHub OAuth authorization URL.

        Args:
            state: The OAuth state parameter for CSRF protection.

        Returns:
            The full authorization URL.
        """
        params = {
            "client_id": self.settings.github_client_id,
            "redirect_uri": f"http://localhost:{self.settings.port}/api/auth/callback",
            "scope": "user:email read:org",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.GITHUB_AUTHORIZE_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> str | None:
        """Exchange an OAuth code for an access token.

        Args:
            code: The authorization code from GitHub.

        Returns:
            The access token, or None if exchange failed.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GITHUB_TOKEN_URL,
                data={
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return data.get("access_token")

    async def get_github_user(self, access_token: str) -> dict | None:
        """Fetch the authenticated user's GitHub profile.

        Args:
            access_token: The GitHub access token.

        Returns:
            The user profile data, or None if request failed.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GITHUB_USER_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                return None

            return response.json()

    def get_or_create_user(
        self,
        github_id: int,
        github_login: str,
        github_name: str | None,
        github_email: str | None,
        github_avatar_url: str | None,
        access_token: str,
    ) -> User:
        """Get or create a user from GitHub OAuth data.

        Args:
            github_id: The GitHub user ID.
            github_login: The GitHub username.
            github_name: The GitHub display name.
            github_email: The GitHub email.
            github_avatar_url: The GitHub avatar URL.
            access_token: The GitHub access token.

        Returns:
            The existing or newly created user.
        """
        statement = select(User).where(User.github_id == github_id)
        user = self.db.exec(statement).first()

        if user:
            # Update existing user
            user.github_login = github_login
            user.github_name = github_name
            user.github_email = github_email
            user.github_avatar_url = github_avatar_url
            user.access_token_hash = hash_token(access_token)
            user.last_login_at = datetime.now(UTC)
            user.updated_at = datetime.now(UTC)
        else:
            # Create new user
            user = User(
                github_id=github_id,
                github_login=github_login,
                github_name=github_name,
                github_email=github_email,
                github_avatar_url=github_avatar_url,
                access_token_hash=hash_token(access_token),
                last_login_at=datetime.now(UTC),
            )
            self.db.add(user)

        self.db.commit()
        self.db.refresh(user)
        return user

    def create_session(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[UserSession, str]:
        """Create a new session for a user.

        Args:
            user: The user to create a session for.
            user_agent: The client user agent.
            ip_address: The client IP address.

        Returns:
            A tuple of (session, raw_token) where raw_token is the
            unhashed token to return to the client.
        """
        token = generate_session_token()
        token_hash = hash_token(token)

        session = UserSession(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(hours=self.settings.session_expiry_hours),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session, token

    def get_session_by_token(self, token: str) -> UserSession | None:
        """Get an active session by its token.

        Args:
            token: The raw (unhashed) session token.

        Returns:
            The session if found and valid, None otherwise.
        """
        token_hash = hash_token(token)
        statement = select(UserSession).where(
            UserSession.token_hash == token_hash,
            UserSession.is_active == True,  # noqa: E712
            UserSession.expires_at > datetime.now(UTC),
        )
        return self.db.exec(statement).first()

    def get_user_by_session_token(self, token: str) -> User | None:
        """Get the user associated with a session token.

        Args:
            token: The raw (unhashed) session token.

        Returns:
            The user if session is valid, None otherwise.
        """
        session = self.get_session_by_token(token)
        if not session:
            return None

        statement = select(User).where(User.id == session.user_id)
        return self.db.exec(statement).first()

    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session by its token.

        Args:
            token: The raw (unhashed) session token.

        Returns:
            True if session was found and invalidated, False otherwise.
        """
        session = self.get_session_by_token(token)
        if not session:
            return False

        session.is_active = False
        session.updated_at = datetime.now(UTC)
        self.db.commit()
        return True

    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user.

        Args:
            user_id: The user ID.

        Returns:
            The number of sessions invalidated.
        """
        statement = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True,  # noqa: E712
        )
        sessions = self.db.exec(statement).all()

        now = datetime.now(UTC)
        for session in sessions:
            session.is_active = False
            session.updated_at = now

        self.db.commit()
        return len(sessions)
