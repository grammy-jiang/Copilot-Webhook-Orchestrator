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

### Backend

| Attribute | Value |
|-----------|-------|
| **Type** | Python web service |
| **Language** | Python 3.12 |
| **Framework** | FastAPI + SQLModel (SQLAlchemy + Pydantic) |
| **Package Manager** | uv (https://github.com/astral-sh/uv) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Test Framework** | pytest (async mode) |

### Frontend

| Attribute | Value |
|-----------|-------|
| **Type** | SPA with SSR support |
| **Language** | TypeScript 5.x |
| **Framework** | SvelteKit 2.x (Svelte 5) |
| **Package Manager** | pnpm |
| **CSS** | Tailwind CSS 3.x |
| **UI Components** | shadcn-svelte |
| **Unit Testing** | Vitest + @testing-library/svelte |
| **E2E Testing** | Playwright |

---

## Build & Validation Commands

**All commands run from repository root.** Use the Makefile; do not run uv/pytest/pnpm directly.

### Required Setup (run once)

**Backend:**
```bash
make install-dev        # Install all dependencies including dev tools
make pre-commit-install # Install pre-commit hooks
```

**Frontend:**
```bash
make frontend-install           # Install all dependencies
make frontend-install-browsers  # Install browser binaries for E2E tests
```

### Development Workflow

**Backend (from repo root):**

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

**Frontend (from repo root):**

| Task | Command |
|------|---------||
| **Start dev server** | `make frontend-dev` |
| **Run unit tests** | `make frontend-test` |
| **Run E2E tests** | `make frontend-test-e2e` |
| **Run all tests** | `make frontend-test-all` |
| **Type check** | `make frontend-check` |
| **Lint code** | `make frontend-lint` |
| **Format code** | `make frontend-format` |
| **Build for production** | `make frontend-build` |

### Validation Before Committing

**ALWAYS run these before declaring work complete:**

**Backend:**
```bash
make test         # All tests must pass
make lint         # Must show "All checks passed!"
make format-check # Must show "files already formatted"
```

**Frontend:**
```bash
make frontend-check     # TypeScript type checking
make frontend-lint      # ESLint checks
make frontend-test      # Unit/component tests
make frontend-test-e2e  # E2E tests (if UI changes)
```

### Coverage Requirements

**Backend:**
- **Core modules** (`app/services/`, `app/api/`): minimum **95%** coverage
- **Other modules**: minimum **85%** coverage
- Run `make test-cov` to verify coverage.

**Frontend:**
- **Components** (`src/lib/components/`): minimum **80%** coverage
- Run `make frontend-test-cov` to verify coverage.

---

## Project Structure

### Backend (`src/backend/`)

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
│   └── services/               # Business logic (auth, crypto, github)
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── unit/                   # Fast isolated tests
│   └── integration/            # API endpoint tests
└── pyproject.toml              # Project config & dependencies
```

### Frontend (`src/frontend/`)

```
src/frontend/                   # SvelteKit frontend application
├── package.json
├── svelte.config.js
├── tailwind.config.js
├── vite.config.ts
├── vitest.config.ts
├── playwright.config.ts
├── src/
│   ├── app.html                # HTML template
│   ├── app.css                 # Global styles, Tailwind imports
│   ├── lib/
│   │   ├── components/         # Svelte components
│   │   │   ├── ui/             # shadcn-svelte components
│   │   │   └── __tests__/      # Component unit tests
│   │   ├── stores/             # Svelte 5 state (runes)
│   │   └── utils/              # Utility functions
│   └── routes/                 # SvelteKit file-based routing
│       ├── +layout.svelte      # Root layout
│       ├── +page.svelte        # Dashboard (home)
│       ├── login/              # Login page
│       ├── repositories/       # Repository pages
│       └── events/             # Event stream pages
├── static/                     # Static assets
└── tests/e2e/                  # Playwright E2E tests
```

### Key Files

**Backend:**
- **Entry point:** `src/backend/app/main.py` → `create_app()`
- **Config:** `src/backend/app/config.py` → `Settings` class (loads `.env`)
- **Routes:** `src/backend/app/api/routers/*.py`
- **Models:** `src/backend/app/db/models/*.py`
- **Test fixtures:** `src/backend/tests/conftest.py`
- **pyproject.toml:** `src/backend/pyproject.toml` (ruff, mypy, pytest, coverage config)

**Frontend:**
- **Entry point:** `src/frontend/src/routes/+layout.svelte`
- **Components:** `src/frontend/src/lib/components/`
- **Stores:** `src/frontend/src/lib/stores/` (Svelte 5 runes)
- **Routes:** `src/frontend/src/routes/` (file-based routing)
- **E2E tests:** `src/frontend/tests/e2e/`
- **UI components:** shadcn-svelte in `src/frontend/src/lib/components/ui/`

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

**Backend:**
- **Framework:** pytest with async mode (`asyncio_mode = "auto"`)
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.security`
- **Fixtures:** Use `conftest.py` fixtures (`client`, `session`, `test_user`, `webhook_secret`)

**Frontend:**
- **Unit/Component:** Vitest + @testing-library/svelte
- **E2E:** Playwright (cross-browser)
- **Test location:** `src/lib/components/__tests__/` for unit, `tests/e2e/` for E2E

When adding code:
1. Write test first (TDD: Red → Green → Refactor)
2. Backend: `tests/unit/` for pure logic, `tests/integration/` for API endpoints
3. Frontend: `__tests__/` folders for unit tests, `tests/e2e/` for E2E
4. Use existing fixtures from `conftest.py` (backend) or test utilities (frontend)

### Adding Dependencies

**Backend:**
```bash
make add pkg=<package>       # Add runtime dependency
make add-dev pkg=<package>   # Add dev dependency
```

**Frontend (from repo root):**
```bash
make frontend-add pkg=<package>       # Add runtime dependency
make frontend-add-dev pkg=<package>   # Add dev dependency
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
make frontend-install && make frontend-install-browsers

# Daily workflow - Backend
make test                 # Run all tests
make lint && make format  # Fix code style
make run                  # Start server at localhost:8000

# Daily workflow - Frontend
make frontend-dev         # Start dev server at localhost:5173
make frontend-test        # Run unit tests
make frontend-check && make frontend-lint  # Type check and lint

# Before committing - Backend
make test && make lint && make format-check

# Before committing - Frontend
make frontend-check && make frontend-lint && make frontend-test

# Adding new backend endpoint
# 1. Add route in src/backend/app/api/routers/
# 2. Add schemas in src/backend/app/api/schemas.py
# 3. Add tests in src/backend/tests/integration/
# 4. Run: make test && make lint

# Adding new frontend component
# 1. Add component in src/frontend/src/lib/components/
# 2. Add tests in src/frontend/src/lib/components/__tests__/
# 3. Run: make frontend-test && make frontend-check
```
