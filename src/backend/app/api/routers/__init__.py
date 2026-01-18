"""API routers package."""

from app.api.routers.auth import router as auth_router
from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.api.routers.installations import router as installations_router
from app.api.routers.repositories import router as repositories_router
from app.api.routers.webhooks import router as webhooks_router

__all__ = [
    "auth_router",
    "events_router",
    "health_router",
    "installations_router",
    "repositories_router",
    "webhooks_router",
]
