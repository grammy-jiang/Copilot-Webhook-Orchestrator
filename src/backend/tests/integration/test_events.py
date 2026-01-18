"""Tests for event storage and retrieval.

These tests verify webhook event storage, querying, and user isolation.
"""

import json

import pytest

from app.db.models.event import Event


class TestEventStorage:
    """Tests for webhook event storage."""

    @pytest.mark.integration
    async def test_store_event_with_all_fields(
        self,
        session,
        test_user,
        test_installation,
        test_repository,
    ):
        """AC: Event stored with all required fields."""
        event = Event(
            delivery_id="store-test-123",
            event_type="pull_request",
            action="opened",
            repository_id=test_repository.id,
            installation_id=test_installation.id,
            user_id=test_user.id,
            payload=json.dumps({"action": "opened", "number": 42}),
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        assert event.id is not None
        assert event.delivery_id == "store-test-123"
        assert event.event_type == "pull_request"
        assert event.action == "opened"
        assert event.processed is False

    @pytest.mark.integration
    async def test_duplicate_delivery_id_rejected(
        self,
        session,
        test_user,
    ):
        """AC: Duplicate delivery IDs are rejected."""
        from sqlalchemy.exc import IntegrityError

        event1 = Event(
            delivery_id="duplicate-test-123",
            event_type="push",
            user_id=test_user.id,
            payload="{}",
        )
        session.add(event1)
        session.commit()

        event2 = Event(
            delivery_id="duplicate-test-123",  # Same delivery ID
            event_type="push",
            user_id=test_user.id,
            payload="{}",
        )
        session.add(event2)

        with pytest.raises(IntegrityError):
            session.commit()


class TestEventRetrieval:
    """Tests for event retrieval and filtering."""

    @pytest.mark.integration
    async def test_list_events_for_user(
        self,
        authenticated_client,
        session,
        test_user,
        test_event,
    ):
        """AC: User can list their events."""
        response = await authenticated_client.get("/api/events")

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data

    @pytest.mark.integration
    async def test_filter_events_by_type(
        self,
        authenticated_client,
        session,
        test_user,
    ):
        """AC: Events can be filtered by type."""
        # Create events of different types
        for event_type in ["push", "pull_request", "issues"]:
            event = Event(
                delivery_id=f"filter-{event_type}-test",
                event_type=event_type,
                user_id=test_user.id,
                payload="{}",
            )
            session.add(event)
        session.commit()

        response = await authenticated_client.get(
            "/api/events", params={"event_type": "push"}
        )

        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["event_type"] == "push"

    @pytest.mark.integration
    async def test_filter_events_by_repository(
        self,
        authenticated_client,
        session,
        test_user,
        test_repository,
    ):
        """AC: Events can be filtered by repository."""
        event = Event(
            delivery_id="repo-filter-test",
            event_type="push",
            repository_id=test_repository.id,
            user_id=test_user.id,
            payload="{}",
        )
        session.add(event)
        session.commit()

        response = await authenticated_client.get(
            "/api/events", params={"repository_id": test_repository.id}
        )

        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["repository_id"] == test_repository.id

    @pytest.mark.integration
    async def test_events_pagination(
        self,
        authenticated_client,
        session,
        test_user,
    ):
        """AC: Events are paginated correctly."""
        # Create 10 events
        for i in range(10):
            event = Event(
                delivery_id=f"pagination-test-{i}",
                event_type="push",
                user_id=test_user.id,
                payload="{}",
            )
            session.add(event)
        session.commit()

        # Get first page
        response1 = await authenticated_client.get(
            "/api/events", params={"limit": 5, "offset": 0}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["events"]) == 5
        assert data1["limit"] == 5
        assert data1["offset"] == 0

        # Get second page
        response2 = await authenticated_client.get(
            "/api/events", params={"limit": 5, "offset": 5}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["events"]) == 5
        assert data2["offset"] == 5

    @pytest.mark.integration
    async def test_get_single_event(
        self,
        authenticated_client,
        session,
        test_user,
        test_event,
    ):
        """AC: User can get single event by ID."""
        response = await authenticated_client.get(f"/api/events/{test_event.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_event.id
        assert data["delivery_id"] == test_event.delivery_id


class TestEventUserIsolation:
    """Tests for event user isolation."""

    @pytest.mark.integration
    async def test_user_cannot_see_other_users_events(
        self,
        app,
        session,
        test_user,
        test_event,
    ):
        """AC: User cannot see events from other users.

        @security AUTHZ-02
        """
        from datetime import UTC, datetime, timedelta

        from httpx import ASGITransport, AsyncClient

        from app.db.models.session import Session as UserSession
        from app.db.models.user import User
        from app.services.crypto import generate_session_token, hash_token

        # Create another user
        other_user = User(
            github_id=88888888,
            github_login="otheruser2",
            github_name="Other User 2",
            github_email="other2@example.com",
            access_token_hash=hash_token("other_token_2"),
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        # Create session for other user
        token = generate_session_token()
        other_session = UserSession(
            user_id=other_user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        session.add(other_session)
        session.commit()

        # Try to get first user's event
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies={"session_token": token},
        ) as client:
            response = await client.get(f"/api/events/{test_event.id}")

        assert response.status_code == 404

    @pytest.mark.integration
    async def test_events_list_only_shows_user_events(
        self,
        app,
        session,
        test_user,
    ):
        """AC: Event list only shows current user's events."""
        from datetime import UTC, datetime, timedelta

        from httpx import ASGITransport, AsyncClient

        from app.db.models.session import Session as UserSession
        from app.db.models.user import User
        from app.services.crypto import generate_session_token, hash_token

        # Create event for test_user
        event1 = Event(
            delivery_id="user1-event",
            event_type="push",
            user_id=test_user.id,
            payload="{}",
        )
        session.add(event1)

        # Create another user with their own event
        other_user = User(
            github_id=77777777,
            github_login="otheruser3",
            github_email="other3@example.com",
            access_token_hash=hash_token("other_token_3"),
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        event2 = Event(
            delivery_id="user2-event",
            event_type="push",
            user_id=other_user.id,
            payload="{}",
        )
        session.add(event2)
        session.commit()

        # Create session for other user
        token = generate_session_token()
        other_session = UserSession(
            user_id=other_user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        session.add(other_session)
        session.commit()

        # List events as other user
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies={"session_token": token},
        ) as client:
            response = await client.get("/api/events")

        assert response.status_code == 200
        data = response.json()

        # Should only see their own event
        delivery_ids = [e["delivery_id"] for e in data["events"]]
        assert "user2-event" in delivery_ids
        assert "user1-event" not in delivery_ids
