"""Health check router."""

from datetime import UTC, datetime

from fastapi import APIRouter

from app import __version__
from app.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns the service health status, version, and current timestamp.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(UTC),
    )
