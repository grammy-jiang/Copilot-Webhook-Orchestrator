"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routers import (
    auth_router,
    events_router,
    health_router,
    installations_router,
    webhooks_router,
)
from app.config import get_settings
from app.db.engine import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Webhook-driven automation service for GitHub Copilot workflow management",
        version=__version__,
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(webhooks_router)
    app.include_router(installations_router)
    app.include_router(events_router)

    @app.on_event("startup")
    async def on_startup() -> None:
        """Initialize the database on startup."""
        init_db()

    return app


# Create the default application instance
app = create_app()
