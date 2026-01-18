# ADR-004: Use `uv` for Python Package Management

**Status:** Accepted

**Date:** January 18, 2026

**Deciders:** @arch-spec-author, @requirements

______________________________________________________________________

## Context

We need a Python package manager and virtual environment tool for:

- Managing dependencies (install, update, lock)
- Creating reproducible builds
- Development and CI/CD environments
- Docker image builds

______________________________________________________________________

## Decision

We will use **`uv`** (from Astral) for Python package management and virtual
environment creation.

______________________________________________________________________

## Options Considered

### Option A: uv (Selected)

**Pros:**

- Extremely fast (10-100x faster than pip)
- Drop-in pip replacement (`uv pip install`)
- Native lockfile support (`uv lock`)
- Built-in virtual environment management (`uv venv`)
- Single binary, easy installation
- Active development by Astral (Ruff maintainers)
- Supports PEP 517/518/621 (`pyproject.toml`)

**Cons:**

- Newer tool (less ecosystem maturity)
- Some edge cases may differ from pip
- Team must learn new commands

### Option B: pip + venv + pip-tools

**Pros:**

- Standard Python tooling
- Well-documented
- pip-compile for lockfiles

**Cons:**

- Slow dependency resolution
- Multiple tools to coordinate
- No single source of truth

### Option C: Poetry

**Pros:**

- All-in-one (venv, deps, build, publish)
- Popular in Python community
- `poetry.lock` for reproducibility

**Cons:**

- Slower than uv
- Non-standard `pyproject.toml` sections (historically)
- Heavier installation

### Option D: PDM

**Pros:**

- PEP 582 support (no venv)
- Standard pyproject.toml
- Good lockfile support

**Cons:**

- Less popular than Poetry
- Slower than uv
- PEP 582 not widely adopted

______________________________________________________________________

## Consequences

### Positive

- Faster CI/CD builds (dependency installation)
- Faster local development iteration
- Modern tooling aligns with Ruff (already using for linting)
- Simple commands (`uv pip install -r requirements.txt`)

### Negative

- Team must learn uv if unfamiliar
- May encounter edge cases not covered by uv yet

### Mitigations

- uv is pip-compatible; fallback to pip if needed
- Lock dependencies with `uv pip compile`
- Document uv commands in CONTRIBUTING.md

______________________________________________________________________

## Implementation Notes

### Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip (for bootstrap)
pip install uv
```

### Common Commands

```bash
# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install from pyproject.toml
uv pip install -e ".[dev]"

# Generate lockfile
uv pip compile pyproject.toml -o requirements.lock

# Sync from lockfile
uv pip sync requirements.lock
```

### pyproject.toml Structure

```toml
[project]
name = "copilot-orchestrator"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "uvicorn>=0.27.0",
    "httpx>=0.26.0",
    "pyjwt>=2.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.lock ./

# Install dependencies
RUN uv pip install --system -r requirements.lock

# Copy application
COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

______________________________________________________________________

## Related Documents

- [Feature One-Pager](../../copilot-workflow-orchestrator-feature-onepager.md)
- [uv Documentation](https://docs.astral.sh/uv/)

______________________________________________________________________

**Decision recorded by:** @arch-spec-author agent
