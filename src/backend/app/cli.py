"""CLI application for the Copilot Webhook Orchestrator."""

import typer
import uvicorn

from app import __version__
from app.config import get_settings
from app.db.engine import init_db

cli_app = typer.Typer(
    name="copilot-orchestrator",
    help="Webhook-driven automation service for GitHub Copilot workflow management",
    no_args_is_help=True,
)


@cli_app.command()
def version() -> None:
    """Show the application version."""
    typer.echo(f"Copilot Webhook Orchestrator v{__version__}")


@cli_app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
) -> None:
    """Start the API server."""
    typer.echo(f"Starting server on {host}:{port}...")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli_app.command()
def init_database() -> None:
    """Initialize the database (create tables)."""
    typer.echo("Initializing database...")
    init_db()
    typer.echo("Database initialized successfully.")


@cli_app.command()
def show_config() -> None:
    """Show the current configuration (without secrets)."""
    settings = get_settings()

    typer.echo("Current Configuration:")
    typer.echo(f"  App Name: {settings.app_name}")
    typer.echo(f"  Environment: {settings.environment}")
    typer.echo(f"  Debug: {settings.debug}")
    typer.echo(f"  Host: {settings.host}")
    typer.echo(f"  Port: {settings.port}")
    typer.echo(f"  Database URL: {_mask_url(settings.database_url)}")
    typer.echo(f"  GitHub App ID: {settings.github_app_id or '(not set)'}")
    typer.echo(f"  GitHub Client ID: {settings.github_client_id or '(not set)'}")
    typer.echo(
        f"  GitHub Client Secret: {'***' if settings.github_client_secret else '(not set)'}"
    )
    typer.echo(
        f"  GitHub Webhook Secret: {'***' if settings.github_webhook_secret else '(not set)'}"
    )
    typer.echo(
        f"  GitHub Private Key: {'***' if settings.github_private_key else '(not set)'}"
    )


def _mask_url(url: str) -> str:
    """Mask sensitive parts of a database URL."""
    if "@" in url:
        # Mask password in URL like postgresql://user:password@host/db
        parts = url.split("@")
        prefix = parts[0]
        if ":" in prefix:
            scheme_user = prefix.rsplit(":", 1)[0]
            return f"{scheme_user}:***@{parts[1]}"
    return url


if __name__ == "__main__":
    cli_app()
