# ADR-001: Use FastAPI with SQLModel for Backend

**Status:** Accepted

**Date:** January 18, 2026

**Deciders:** @arch-spec-author, @requirements

______________________________________________________________________

## Context

We need to choose a Python web framework and ORM for the Copilot Workflow
Orchestrator backend. The backend must:

- Handle GitHub webhooks with signature verification
- Serve REST API for the SvelteKit frontend
- Persist data to SQLite (dev) and PostgreSQL (prod)
- Support async operations for concurrent webhook processing
- Generate OpenAPI documentation automatically

______________________________________________________________________

## Decision

We will use **FastAPI** as the web framework and **SQLModel** as the ORM.

______________________________________________________________________

## Options Considered

### Option A: FastAPI + SQLModel (Selected)

**Pros:**

- Native async support (ASGI)
- Automatic OpenAPI/Swagger generation
- Pydantic integration for validation
- SQLModel unifies Pydantic models and SQLAlchemy
- Type hints throughout
- Modern Python patterns
- Excellent documentation
- Active community

**Cons:**

- Smaller ecosystem than Django
- Less "batteries included" (no admin, auth, etc.)
- SQLModel is newer (less battle-tested than pure SQLAlchemy)

### Option B: Django + Django REST Framework

**Pros:**

- Mature ecosystem
- Built-in admin interface
- Built-in auth system
- Django ORM is stable

**Cons:**

- Sync by default (Django 4+ has async, but ecosystem is mostly sync)
- Heavier framework (more opinions, more boilerplate)
- Separate validation layer (DRF serializers)
- No native OpenAPI generation

### Option C: Flask + SQLAlchemy

**Pros:**

- Lightweight, flexible
- Mature SQLAlchemy ORM
- Large ecosystem

**Cons:**

- No native async support
- No built-in validation
- Manual OpenAPI setup (flask-openapi3, connexion, etc.)
- More boilerplate for REST APIs

______________________________________________________________________

## Consequences

### Positive

- Async webhook handling improves throughput
- OpenAPI spec generated from code (contract-first)
- Single model definitions for DB and API (SQLModel)
- Type safety catches errors at development time
- Fast development iteration

### Negative

- Team must learn FastAPI patterns if unfamiliar
- SQLModel is less mature; may need to drop to SQLAlchemy for complex queries
- No built-in admin (will use CLI + SQL client)

### Mitigations

- SQLModel allows raw SQLAlchemy access when needed
- Alembic for migrations (same as SQLAlchemy)
- Structured logging and health endpoints for observability

______________________________________________________________________

## Related Documents

- [Phase 1 Architecture Brief](../phase-1-architecture-brief.md)
- [Phase 1 Data Model](../phase-1-data-model.md)

______________________________________________________________________

**Decision recorded by:** @arch-spec-author agent
