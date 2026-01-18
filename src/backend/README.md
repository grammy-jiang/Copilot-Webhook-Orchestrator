# Copilot Webhook Orchestrator - Backend

Backend service for the Copilot Webhook Orchestrator.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Package Manager**: uv

## Development

See the root [Makefile](../../Makefile) for available commands.

```bash
# From repository root
make setup      # Create venv and install dependencies
make test       # Run tests
make run        # Start development server
```
