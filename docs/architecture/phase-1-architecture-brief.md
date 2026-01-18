# Phase 1 Architecture Brief — Copilot Workflow Orchestrator

**Status:** Architecture Design

**Date:** January 18, 2026

**Agent:** @arch-spec-author

**Phase:** Phase 1 (Event Stream + Dashboard + Authentication)

______________________________________________________________________

## 1. Context

### 1.1 Problem Statement

GitHub Copilot Coding Agent automates implementation work, but developers still
perform repetitive manual GitHub workflow tasks (assigning issues, requesting
reviews, tracking state). This tool automates the workflow orchestration layer
via webhook-driven event processing.

### 1.2 Scope

Phase 1 establishes the **foundation**: reliable GitHub integration,
observability via event stream, and a minimal dashboard UI.

**In Scope:**

- User authentication via GitHub OAuth
- GitHub App installation and repository access
- Webhook receiver with signature verification
- Event stream storage and retrieval
- Repository selection UI
- Event stream viewer
- Minimal dashboard
- CLI commands for local/Docker operation

**Out of Scope:**

- State machine automation (Phase 3)
- Automated actions (Phase 3)
- AI assistance (Phase 5)
- Multi-installation support (Phase 6+)

______________________________________________________________________

## 2. Goals and Non-Goals

### 2.1 Goals

| Goal                       | Success Metric                                  |
| -------------------------- | ----------------------------------------------- |
| Reliable webhook ingestion | Zero missed events (idempotent processing)      |
| Complete event history     | 1-year retention with efficient querying        |
| Secure authentication      | GitHub OAuth with session management            |
| Operational visibility     | Dashboard load time ≤5 seconds                  |
| Developer experience       | CLI for local development and Docker deployment |

### 2.2 Non-Goals

- Modifying or analyzing source code diffs
- Editing GitHub Actions workflows
- Fully autonomous merging
- Multi-tenant/multi-installation support
- Real-time collaboration features

______________________________________________________________________

## 3. Constraints

### 3.1 Technical Constraints

| Constraint               | Value                            | Rationale                                          |
| ------------------------ | -------------------------------- | -------------------------------------------------- |
| Backend Framework        | FastAPI                          | Async support, OpenAPI generation, modern Python   |
| ORM                      | SQLModel                         | Pydantic integration, type safety, SQLAlchemy core |
| Frontend Framework       | SvelteKit 2.x (Svelte 5)         | Reactive runes, SSR support, lightweight           |
| UI Components            | shadcn-svelte                    | Accessible, headless, Tailwind-based               |
| CSS Framework            | Tailwind CSS                     | Utility-first, rapid development                   |
| Database (Dev)           | SQLite                           | Zero-config local development                      |
| Database (Prod)          | PostgreSQL                       | ACID, JSONB, production-grade                      |
| Backend Package Manager  | uv                               | Fast, modern Python dependency management          |
| Frontend Package Manager | pnpm                             | Fast, disk-efficient Node.js package management    |
| Frontend Testing (Unit)  | Vitest + @testing-library/svelte | Fast, ESM-native, component testing                |
| Frontend Testing (E2E)   | Playwright                       | Cross-browser E2E, accessibility testing           |
| Deployment               | Docker Compose                   | Full-stack local and production deployment         |

### 3.2 Integration Constraints

| System          | Integration Method | Notes                                  |
| --------------- | ------------------ | -------------------------------------- |
| GitHub API      | REST API v3        | Installation access tokens (JWT-based) |
| GitHub Webhooks | HTTPS POST         | HMAC-SHA256 signature verification     |
| GitHub OAuth    | OAuth 2.0          | User authentication (not app auth)     |

### 3.3 Scale Constraints

| Metric          | Target                        | Notes                       |
| --------------- | ----------------------------- | --------------------------- |
| Repositories    | ≤10 (MVP), design for 50+     | Single concurrency per repo |
| Events/minute   | ~30 (10 repos × 3 events/min) | 43K events/day              |
| Event retention | 1 year                        | ~15M events total at scale  |
| Dashboard load  | ≤3 seconds                    | Paginated queries           |

______________________________________________________________________

## 4. Quality Attributes (NFRs)

### 4.1 Security

| Requirement          | Implementation                                          |
| -------------------- | ------------------------------------------------------- |
| Authentication       | GitHub OAuth 2.0 with secure session cookies            |
| Authorization        | User can only access their own installations/repos      |
| Webhook verification | HMAC-SHA256 signature validation (mandatory)            |
| Secrets management   | Environment variables / secret manager (not code)       |
| Session security     | HTTP-only, Secure, SameSite cookies                     |
| CSRF protection      | Token-based CSRF protection on state-changing endpoints |

### 4.2 Reliability

| Requirement          | Implementation                                      |
| -------------------- | --------------------------------------------------- |
| Idempotency          | Delivery ID deduplication on webhook ingestion      |
| Graceful degradation | Return 200/202 to GitHub immediately, process async |
| Error handling       | Fail-closed; log errors with context                |
| Data durability      | PostgreSQL with WAL; SQLite with journaling         |

### 4.3 Performance

| Requirement           | Target                             |
| --------------------- | ---------------------------------- |
| Webhook response time | \<500ms (200 OK returned fast)     |
| Event storage latency | \<100ms per event                  |
| Dashboard load time   | \<3 seconds (paginated)            |
| Event stream query    | \<500ms for 50 events with filters |

### 4.4 Observability

| Requirement        | Implementation                                   |
| ------------------ | ------------------------------------------------ |
| Health endpoint    | `GET /health` with DB connectivity check         |
| Structured logging | JSON logs with request_id, event context         |
| Metrics            | Event count, processing latency, error rate      |
| Error tracking     | Stack traces with context (not exposed to users) |

______________________________________________________________________

## 5. Architecture Overview

### 5.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1 ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────────┐
│   GitHub    │────▶│  Webhook    │────▶│         FastAPI Backend         │
│  Platform   │     │  Receiver   │     │  ┌─────────┬─────────┬────────┐ │
└─────────────┘     └─────────────┘     │  │  Auth   │  Events │  API   │ │
                                        │  │ Service │ Service │ Routes │ │
┌─────────────┐                         │  └────┬────┴────┬────┴───┬────┘ │
│   Browser   │◀───────────────────────▶│       │         │        │      │
│  (SvelteKit)│                         └───────┼─────────┼────────┼──────┘
└─────────────┘                                 │         │        │
                                                ▼         ▼        ▼
                                        ┌─────────────────────────────────┐
                                        │   PostgreSQL / SQLite (SQLModel)│
                                        │  ┌───────┬───────┬───────────┐  │
                                        │  │ Users │Events │ Installs  │  │
                                        │  └───────┴───────┴───────────┘  │
                                        └─────────────────────────────────┘
```

### 5.2 Component Responsibilities

| Component                  | Responsibility                                                  |
| -------------------------- | --------------------------------------------------------------- |
| **Webhook Receiver**       | Receive GitHub webhooks, verify signature, queue for processing |
| **Auth Service**           | GitHub OAuth flow, session management, user lookup              |
| **Events Service**         | Store events, query with filters, deduplication                 |
| **API Routes**             | REST endpoints for frontend (repos, events, dashboard)          |
| **SvelteKit 2.x Frontend** | Repository list, event stream viewer, dashboard (shadcn-svelte) |
| **Database**               | Persist users, sessions, installations, repositories, events    |

______________________________________________________________________

## 6. Key Design Decisions

### 6.1 Synchronous vs Asynchronous Webhook Processing

**Decision:** Synchronous processing with fast acknowledgment.

**Rationale:**

- Phase 1 event volume is low (~30 events/min)
- Simplifies architecture (no message queue needed)
- Return 200 OK immediately after signature verification
- Process and store event in same request (fast enough)

**Future:** Add background queue (Redis/RabbitMQ) in Phase 3+ if needed.

### 6.2 Session Storage

**Decision:** Database-backed sessions (not Redis).

**Rationale:**

- Fewer moving parts in Phase 1
- SQLModel already available
- Session table with expiry and cleanup
- Can migrate to Redis later if needed

### 6.3 Frontend-Backend Communication

**Decision:** REST API with JSON responses.

**Rationale:**

- Simple and well-understood
- FastAPI auto-generates OpenAPI docs
- SvelteKit can fetch during SSR or client-side
- GraphQL adds complexity without Phase 1 benefit

### 6.4 Database Abstraction

**Decision:** SQLModel with SQLite (dev) / PostgreSQL (prod).

**Rationale:**

- Single ORM for both databases
- Pydantic models double as API schemas
- Type-safe queries
- Easy migration via Alembic

______________________________________________________________________

## 7. Open Questions

| Question                                                               | Owner | Status |
| ---------------------------------------------------------------------- | ----- | ------ |
| Webhook retry handling: queue failed events or rely on GitHub retries? | TBD   | Open   |
| Real-time updates: polling vs SSE vs WebSocket for event stream?       | TBD   | Open   |
| Session refresh: sliding expiration or fixed?                          | TBD   | Open   |
| Large payload storage: inline JSONB or external object storage?        | TBD   | Open   |

______________________________________________________________________

## 8. Risk Register

| Risk                           | Likelihood | Impact   | Mitigation                                          |
| ------------------------------ | ---------- | -------- | --------------------------------------------------- |
| GitHub API rate limiting       | Medium     | Medium   | Cache installation tokens; implement backoff        |
| Webhook signature spoofing     | Low        | Critical | Mandatory HMAC-SHA256 verification                  |
| Database connection exhaustion | Low        | High     | Connection pooling; health checks                   |
| Session hijacking              | Low        | High     | Secure cookies; CSRF tokens; short expiry           |
| Event retention bloat          | Medium     | Medium   | Indexing; archival strategy; configurable retention |

______________________________________________________________________

## 9. Deliverables

### Phase 1 Architecture Artifacts

| Artifact           | Path                                              | Status |
| ------------------ | ------------------------------------------------- | ------ |
| Architecture Brief | `docs/architecture/phase-1-architecture-brief.md` | ✅     |
| System Diagrams    | `docs/architecture/diagrams/`                     | 🔄     |
| OpenAPI Contract   | `docs/architecture/api/openapi.yaml`              | 🔄     |
| Data Model         | `docs/architecture/data-model.md`                 | 🔄     |
| ADRs               | `docs/architecture/adr/`                          | 🔄     |

______________________________________________________________________

## 10. Next Steps

1. Generate system diagrams (C4 context, container, sequence)
1. Draft OpenAPI contract with all Phase 1 endpoints
1. Define SQLModel data models with relationships
1. Write ADRs for key decisions
1. Handoff to `@risk-and-nfr-gate` for security review

______________________________________________________________________

**Document generated by:** @arch-spec-author agent

**Input documents:**

- [Feature One-Pager](../copilot-workflow-orchestrator-feature-onepager.md)
- [Phase 1 User Stories](../phase-1-user-stories.md)
- [Requirements Document](../copilot-workflow-orchestrator-requirements.md)
