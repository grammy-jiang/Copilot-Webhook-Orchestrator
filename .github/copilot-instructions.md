# Copilot Coding Agent Instructions

This file provides repository-wide instructions for GitHub Copilot coding agents.
**Trust these instructions.** Only search or explore if information here is incomplete or in error.

---

## Custom Agent Usage

This repository contains multiple custom agents in `.github/agents/` for different use cases.

**ALWAYS follow this protocol:**
1. **At the beginning** of every reply, explicitly state which custom agent you are using
2. **At the end** of every reply, confirm which custom agent was used
3. **If work is complete**, recommend which custom agent should be used in the next step

---

## Repository Overview

**Copilot Webhook Orchestrator** — A webhook-driven automation service for GitHub Copilot workflow management.

| Attribute | Value |
|-----------|-------|
| **Type** | Python web service (FastAPI backend) |
| **Language** | Python 3.12 |
| **Framework** | FastAPI + SQLModel (SQLAlchemy + Pydantic) |
| **Package Manager** | uv (https://github.com/astral-sh/uv) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Test Framework** | pytest (async mode) |

---

## Build & Validation Commands

**All commands run from repository root.** Use the Makefile; do not run uv/pytest directly.

### Required Setup (run once)

```bash
make install-dev        # Install all dependencies including dev tools
make pre-commit-install # Install pre-commit hooks
```

### Development Workflow

| Task | Command |
|------|---------|
| **Run all tests** | `make test` |
| **Run tests with coverage** | `make test-cov` |
| **Run unit tests only** | `make test-unit` |
| **Run integration tests only** | `make test-integration` |
| **Lint code** | `make lint` |
| **Format code** | `make format` |
| **Fix lint issues** | `make lint-fix` |
| **Format + lint fix** | `make fix` |
| **Run dev server** | `make run` |

### Validation Before Committing

**ALWAYS run these before declaring work complete:**

```bash
make test         # All tests must pass
make lint         # Must show "All checks passed!"
make format-check # Must show "files already formatted"
```

### Coverage Requirements

- **Core modules** (`app/services/`, `app/api/`): minimum **95%** coverage
- **Other modules**: minimum **85%** coverage

Run `make test-cov` to verify coverage.

---

## Project Structure

```
src/backend/                    # Python backend application
├── app/                        # Main application package
│   ├── main.py                 # FastAPI app factory (create_app)
│   ├── config.py               # Pydantic Settings (env vars)
│   ├── cli.py                  # Typer CLI commands
│   ├── api/
│   │   ├── routers/            # FastAPI route handlers
│   │   │   ├── auth.py         # OAuth & session endpoints
│   │   │   ├── events.py       # Webhook events endpoints
│   │   │   ├── health.py       # Health check endpoint
│   │   │   ├── installations.py # GitHub App installations
│   │   │   └── webhooks.py     # Webhook receiver
│   │   ├── deps.py             # Dependency injection
│   │   └── schemas.py          # Pydantic request/response models
│   ├── db/
│   │   ├── engine.py           # SQLModel engine & session
│   │   └── models/             # SQLModel ORM models
│   │       ├── user.py, session.py, event.py, installation.py, repository.py
│   └── services/
│       ├── auth.py             # OAuth/session logic
│       ├── crypto.py           # HMAC, JWT, encryption
│       └── github.py           # GitHub API client
├── tests/
│   ├── conftest.py             # Shared fixtures (client, session, user)
│   ├── unit/                   # Fast isolated tests
│   └── integration/            # API endpoint tests
└── pyproject.toml              # Project config & dependencies
```

### Key Files

- **Entry point:** `src/backend/app/main.py` → `create_app()`
- **Config:** `src/backend/app/config.py` → `Settings` class (loads `.env`)
- **Routes:** `src/backend/app/api/routers/*.py`
- **Models:** `src/backend/app/db/models/*.py`
- **Test fixtures:** `src/backend/tests/conftest.py`
- **pyproject.toml:** `src/backend/pyproject.toml` (ruff, mypy, pytest, coverage config)

---

## Code Standards

### Python Style

- **Line length:** 88 chars (ruff/black)
- **Imports:** isort with black profile, first-party package is `app`
- **Type hints:** Required for all functions (strict mypy config exists but not enforced in CI)
- **Docstrings:** Google style
- **No print statements:** Use logging (enforced by ruff T20 rule)

### Test-Driven Development (TDD)

When implementing features:
1. **Red**: Write a failing test first
2. **Green**: Write minimal code to pass the test
3. **Refactor**: Improve structure while keeping tests green

Tests must be:
- **Deterministic**: Fixed clocks, seeded randomness, hermetic fixtures
- **Behavioral**: Test user-visible outcomes, not implementation details
- **Layered**: Unit (many, fast) → Integration (some) → E2E (few, critical paths)

### Testing

- **Framework:** pytest with async mode (`asyncio_mode = "auto"`)
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.security`
- **Fixtures:** Use `conftest.py` fixtures (`client`, `session`, `test_user`, `webhook_secret`)

When adding code:
1. Write test first (TDD: Red → Green → Refactor)
2. Tests in `tests/unit/` for pure logic, `tests/integration/` for API endpoints
3. Use existing fixtures from `conftest.py`

### Adding Dependencies

```bash
make add pkg=<package>       # Add runtime dependency
make add-dev pkg=<package>   # Add dev dependency
```

---

## Issue Templates & Workflow

When generating GitHub Issues, use templates in `.github/ISSUE_TEMPLATE/`:

| Template | Use When |
|----------|----------|
| `01-feature-request.yml` | Proposing new features |
| `02-user-story.yml` | Creating backlog stories |
| `03-bug-report.yml` | Reporting bugs |
| `04-architecture-decision.yml` | Documenting ADRs |
| `05-technical-debt.yml` | Tracking tech debt |
| `06-test-case-gap.yml` | Missing test coverage |
| `07-release-request.yml` | Requesting releases |
| `08-incident-report.yml` | Post-incident reviews |

### Acceptance Criteria Format

Use **Given/When/Then** (Gherkin) format. Always include edge cases:
- Empty/null/missing data states
- Permission/authorization failures
- Validation failures
- Network/timeout errors

---

## Configuration

### Environment Variables

App reads from `.env` file or environment. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_APP_ID` | "" | GitHub App ID |
| `GITHUB_CLIENT_ID` | "" | OAuth Client ID |
| `GITHUB_CLIENT_SECRET` | "" | OAuth Client Secret |
| `GITHUB_WEBHOOK_SECRET` | "" | Webhook HMAC secret |
| `DATABASE_URL` | `sqlite:///./orchestrator.db` | Database connection |
| `DEBUG` | `false` | Enable debug mode |

### Linting Configuration

All in `src/backend/pyproject.toml`:
- **ruff:** Select E, W, F, I, B, C4, UP, S, T20; ignore E501, B008
- **isort:** Black profile, first-party = `app`
- **mypy:** Strict mode (not enforced), Python 3.12 target

---

## Documentation & Resources

- **Issue templates:** `.github/ISSUE_TEMPLATE/*.yml`
- **Agents:** `.github/agents/*.agent.md`
- **Architecture docs:** `docs/architecture/`
- **Best practices:** `docs/best_practices/`

---

## Quick Reference

```bash
# Full dev setup (first time)
make install-dev && make pre-commit-install

# Daily workflow
make test                 # Run all tests
make lint && make format  # Fix code style
make run                  # Start server at localhost:8000

# Before committing
make test && make lint && make format-check

# Adding new endpoint
# 1. Add route in src/backend/app/api/routers/
# 2. Add schemas in src/backend/app/api/schemas.py
# 3. Add tests in src/backend/tests/integration/
# 4. Run: make test && make lint
```
