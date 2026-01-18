# AGENTS.md — Backend (Python/FastAPI)

> Backend-specific agent guidance. For repo-wide rules, see
> [`../../AGENTS.md`](../../AGENTS.md) and
> [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md).

---

## Environment

- **Python:** 3.12 (see `pyproject.toml`)
- **Package Manager:** uv (do not use pip directly)
- **Virtualenv:** `.venv/` (managed by uv)

### Setup Commands

```bash
# From repository root (not this folder!)
make install-dev        # Install all dependencies
make pre-commit-install # Install pre-commit hooks
```

---

## Development Commands

All commands run from **repository root** via Makefile:

| Task | Command |
|------|---------|
| Run tests | `make test` |
| Run tests with coverage | `make test-cov` |
| Unit tests only | `make test-unit` |
| Integration tests only | `make test-integration` |
| Lint | `make lint` |
| Format | `make format` |
| Type check | `make typecheck` |
| Run server | `make run` |

---

## Directory Structure

```
app/                    # Main application package
├── main.py             # FastAPI app factory (create_app)
├── config.py           # Pydantic Settings
├── cli.py              # Typer CLI commands
├── api/
│   ├── routers/        # Route handlers (one file per resource)
│   ├── deps.py         # Dependency injection
│   └── schemas.py      # Pydantic request/response models
├── db/
│   ├── engine.py       # SQLModel engine & session
│   └── models/         # ORM models (one file per entity)
└── services/           # Business logic (auth, crypto, github)

tests/
├── conftest.py         # Shared fixtures
├── unit/               # Fast isolated tests
└── integration/        # API endpoint tests
```

---

## Code Patterns

### Adding a New Endpoint

1. Create route handler in `app/api/routers/<resource>.py`
2. Add schemas in `app/api/schemas.py`
3. Register router in `app/main.py` if new file
4. Write tests in `tests/integration/test_<resource>.py`
5. Validate: `make test && make lint`

### Adding a New Model

1. Create model in `app/db/models/<entity>.py`
2. Import in `app/db/models/__init__.py`
3. Add migration if using Alembic (not yet configured)
4. Write unit tests for model logic
5. Validate: `make test && make lint`

### Adding a New Service

1. Create service in `app/services/<name>.py`
2. Use dependency injection via `app/api/deps.py`
3. Write unit tests in `tests/unit/test_<name>.py`
4. Validate: `make test && make lint`

---

## Testing

### Test-Driven Development (TDD)

1. **Red:** Write a failing test first
2. **Green:** Write minimal code to pass
3. **Refactor:** Improve while keeping tests green

### Test Requirements

- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`
- Use fixtures from `tests/conftest.py` (`client`, `session`, `test_user`)
- Mock external services (HTTP, GitHub API)
- Freeze time where needed (`freezegun` or similar)

### Coverage Targets

- `app/services/`, `app/api/`: **95%** minimum
- Other modules: **85%** minimum

---

## Python Style

- **Type hints:** Required for all public functions
- **Docstrings:** Google style
- **Imports:** isort with black profile
- **Line length:** 88 chars
- **No print statements:** Use `logging` module

### Error Handling

```python
# Good: Explicit exceptions with context
raise ValueError(f"Invalid webhook signature for event {event_id}")

# Bad: Silent failures
try:
    process_webhook(data)
except Exception:
    pass  # Never do this
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("Processing webhook", extra={"event_id": event_id})

# Bad: Never log secrets
logger.debug(f"Token: {api_token}")  # NEVER
```

---

## Files to Avoid Modifying

Unless explicitly required:

- `uv.lock` — dependency lockfile
- `htmlcov/` — generated coverage reports
- `.venv/` — virtual environment
- `__pycache__/` — Python bytecode cache
- `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` — tool caches

---

## Validation Checklist

Before declaring work complete:

```bash
make test         # ✓ All tests pass
make lint         # ✓ "All checks passed!"
make format-check # ✓ "files already formatted"
make test-cov     # ✓ Coverage meets targets
```
