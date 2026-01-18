# Risk & NFR Review: Phase 1 Architecture

**Agent:** @risk-and-nfr-gate

**Date:** January 18, 2026

**Reviewed Documents:**

- [phase-1-architecture-brief.md](phase-1-architecture-brief.md)
- [phase-1-api-contract.md](phase-1-api-contract.md)
- [phase-1-data-model.md](phase-1-data-model.md)
- [phase-1-diagrams.md](phase-1-diagrams.md)
- [ADR-001 through ADR-004](adr/)

______________________________________________________________________

## Verdict: ✅ APPROVED (with Recommendations)

The Phase 1 architecture meets security and NFR requirements for MVP scope. All
high-severity items have mitigations defined. Recommendations below should be
addressed during implementation.

______________________________________________________________________

## 1. Threat Model Summary

### 1.1 Assets Inventory

| Asset                 | Sensitivity | Location         | Protection                    |
| --------------------- | ----------- | ---------------- | ----------------------------- |
| GitHub OAuth tokens   | Critical    | `users` table    | Encrypted at rest             |
| Session tokens        | High        | `user_sessions`  | Hashed (bcrypt/SHA-256)       |
| Webhook payloads      | Medium      | `event_receipts` | JSONB, contains repo metadata |
| User email addresses  | Medium      | `users` table    | Optional, from GitHub OAuth   |
| Installation metadata | Low         | `installations`  | Permissions snapshot          |

### 1.2 Entry Points

| Entry Point             | Authentication        | Trust Level | Risk   |
| ----------------------- | --------------------- | ----------- | ------ |
| `GET /health`           | None                  | Public      | Low    |
| `GET /auth/login`       | None                  | Public      | Medium |
| `GET /auth/callback`    | OAuth state token     | Semi-trust  | Medium |
| `POST /webhooks/github` | HMAC-SHA256 signature | Trusted     | High   |
| All other `/api/*`      | Session cookie        | Trusted     | Medium |

### 1.3 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TRUST BOUNDARY 1                             │
│                      (Public Internet)                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   Browser   │    │   GitHub    │    │  Attacker   │              │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘              │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TRUST BOUNDARY 2                             │
│                   (Application Edge - FastAPI)                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  - Session validation                                        │    │
│  │  - HMAC signature verification                               │    │
│  │  - CSRF token validation                                     │    │
│  │  - Rate limiting (TBD)                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TRUST BOUNDARY 3                             │
│                        (Database Layer)                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  - Encrypted connections (TLS in prod)                       │    │
│  │  - Parameterized queries (SQLModel/SQLAlchemy)               │    │
│  │  - Column-level encryption (access_token)                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.4 Attack Vectors Analysis

| Vector                 | Threat                        | Severity | Mitigation Status    |
| ---------------------- | ----------------------------- | -------- | -------------------- |
| SQL Injection          | Data breach                   | Critical | ✅ SQLModel ORM      |
| XSS                    | Session theft                 | High     | ✅ SvelteKit escapes |
| CSRF                   | Unauthorized state changes    | High     | ⚠️ Specified, verify |
| Webhook Spoofing       | Fake events injected          | Critical | ✅ HMAC-SHA256       |
| Session Hijacking      | Account takeover              | High     | ✅ Secure cookies    |
| OAuth State Tampering  | CSRF on OAuth flow            | High     | ✅ State token       |
| Privilege Escalation   | Access other users' data      | High     | ✅ user_id scoping   |
| Rate Limit Bypass      | DoS / resource exhaustion     | Medium   | ⚠️ Not specified     |
| Timing Attack          | Token enumeration             | Medium   | ⚠️ Use constant-time |
| Information Disclosure | Sensitive data in logs/errors | Medium   | ⚠️ Verify logging    |

______________________________________________________________________

## 2. Abuse Cases Identified

| Abuse Case                 | Risk Level | Mitigation Required                                 | Owner |
| -------------------------- | ---------- | --------------------------------------------------- | ----- |
| Webhook flood attack       | High       | Rate limit `/webhooks/github` (100/min recommended) | Dev   |
| Session token brute force  | Medium     | Rate limit login, use long random tokens (256-bit)  | Dev   |
| Stale session exploitation | Medium     | 30-day max expiry + sliding expiration              | Dev   |
| Event enumeration via IDOR | Low        | All queries scoped to `user_id`                     | Dev   |
| Large payload DoS          | Medium     | Max body size 10MB, reject oversized payloads       | Dev   |
| OAuth code replay          | Low        | State tokens are single-use                         | Dev   |
| Log injection              | Low        | Sanitize log inputs, use structured logging         | Dev   |

______________________________________________________________________

## 3. NFR Completeness Check

### 3.1 Security ✅

| Requirement              | Status | Notes                                          |
| ------------------------ | ------ | ---------------------------------------------- |
| Authentication defined   | ✅     | GitHub OAuth 2.0                               |
| Authorization model      | ✅     | User-scoped access via `user_id` FK            |
| Input validation rules   | ⚠️     | Need Pydantic validators on all inputs         |
| Secrets management       | ✅     | Environment variables, not in code             |
| Audit logging            | ⚠️     | Need to log: login, logout, webhook processing |
| Token encryption at rest | ✅     | `access_token` encrypted                       |
| Session token hashing    | ✅     | bcrypt or SHA-256 specified                    |
| CSRF protection          | ✅     | Documented for state-changing endpoints        |

### 3.2 Performance ✅

| Requirement        | Status | Target          | Notes                           |
| ------------------ | ------ | --------------- | ------------------------------- |
| Latency targets    | ✅     | \<500ms webhook | Documented                      |
| Throughput         | ✅     | ~30 events/min  | Documented                      |
| Rate limiting      | ⚠️     | Not specified   | **Recommendation: Add**         |
| Concurrency limits | ⚠️     | Not specified   | DB connection pool size needed  |
| Caching strategy   | ✅     | N/A for Phase 1 | Deferred, appropriate for scope |
| Pagination         | ✅     | All list APIs   | Implemented with limits         |

### 3.3 Reliability ✅

| Requirement              | Status | Notes                                   |
| ------------------------ | ------ | --------------------------------------- |
| Availability target      | ⚠️     | Not explicitly stated (recommend 99.5%) |
| Failure modes identified | ✅     | Risk register in architecture brief     |
| Retry strategy           | ✅     | Rely on GitHub retries (Phase 1)        |
| Graceful degradation     | ✅     | Return 200 OK quickly                   |
| Idempotency              | ✅     | `delivery_id` deduplication             |

### 3.4 Observability ✅

| Requirement            | Status | Notes                                     |
| ---------------------- | ------ | ----------------------------------------- |
| Health endpoint        | ✅     | `GET /health` with DB check               |
| Structured logging     | ✅     | JSON logs with request_id                 |
| Metrics                | ⚠️     | Specified but not detailed (add counters) |
| Error tracking         | ✅     | Stack traces not exposed to users         |
| Alerting thresholds    | ⚠️     | Not defined (Phase 1 acceptable)          |
| Dashboard requirements | ✅     | Event stream viewer documented            |

______________________________________________________________________

## 4. Migration & Rollback Assessment

| Risk                           | Severity | Mitigation                                    |
| ------------------------------ | -------- | --------------------------------------------- |
| Initial deployment failure     | Medium   | Docker Compose rollback, no data to lose      |
| Database schema migration      | Low      | Alembic migrations with `downgrade()` support |
| Session invalidation on deploy | Low      | Acceptable for Phase 1 (users re-login)       |
| Event data loss                | High     | PostgreSQL WAL enabled, regular backups       |
| Rollback data corruption       | Low      | Additive migrations only, no destructive DDL  |

### Rollback Procedure (Phase 1)

1. Stop FastAPI container
1. Revert Docker image tag
1. Run `alembic downgrade -1` if schema changed
1. Restart container
1. Verify `/health` endpoint

______________________________________________________________________

## 5. Blocking Issues

**None.** All critical security controls are defined.

______________________________________________________________________

## 6. Recommendations

### 6.1 High Priority (Before Implementation)

| #   | Recommendation                                                                         | Category    |
| --- | -------------------------------------------------------------------------------------- | ----------- |
| 1   | **Add rate limiting** to `/webhooks/github` (100 req/min) and `/auth/*` (10 req/min)   | Security    |
| 2   | **Define connection pool size** (recommend 10-20 connections for SQLAlchemy)           | Performance |
| 3   | **Add audit logging** for: login, logout, installation created/deleted, webhook errors | Security    |
| 4   | **Use constant-time comparison** for session token and HMAC verification               | Security    |

### 6.2 Medium Priority (During Implementation)

| #   | Recommendation                                                                | Category      |
| --- | ----------------------------------------------------------------------------- | ------------- |
| 5   | **Add Pydantic validators** for all user inputs (max lengths, regex patterns) | Security      |
| 6   | **Set max request body size** to 10MB to prevent DoS                          | Reliability   |
| 7   | **Add `request_id`** to all log entries for traceability                      | Observability |
| 8   | **Define availability target** as 99.5% uptime for Phase 1                    | Reliability   |
| 9   | **Document log sanitization** rules (no tokens, no passwords in logs)         | Security      |

### 6.3 Low Priority (Post-MVP)

| #   | Recommendation                                         | Category      |
| --- | ------------------------------------------------------ | ------------- |
| 10  | Consider Content-Security-Policy headers for SvelteKit | Security      |
| 11  | Add prometheus metrics endpoint for event counters     | Observability |
| 12  | Implement session rotation on privilege changes        | Security      |

______________________________________________________________________

## 7. Test Requirements

Each risk category requires corresponding tests:

### 7.1 Security Tests

- [ ] **AUTH-01**: Verify unauthenticated access to protected endpoints returns
  401
- [ ] **AUTH-02**: Verify session cookie has `HttpOnly`, `Secure`,
  `SameSite=Lax` flags
- [ ] **AUTH-03**: Verify OAuth state token is validated and single-use
- [ ] **AUTH-04**: Verify CSRF token is required for POST/PUT/DELETE endpoints
- [ ] **WEBHOOK-01**: Verify invalid HMAC signature returns 401
- [ ] **WEBHOOK-02**: Verify missing signature header returns 401
- [ ] **WEBHOOK-03**: Verify duplicate `delivery_id` is rejected (idempotency)
- [ ] **AUTHZ-01**: Verify user cannot access another user's installations
- [ ] **AUTHZ-02**: Verify user cannot access events from non-owned repositories

### 7.2 Performance Tests

- [ ] **PERF-01**: Webhook processing completes in \<500ms (p95)
- [ ] **PERF-02**: Dashboard API returns in \<3 seconds with 50 repos
- [ ] **PERF-03**: Event list with 1000 events returns in \<500ms (paginated)

### 7.3 Reliability Tests

- [ ] **REL-01**: Verify `/health` returns 503 when database is unavailable
- [ ] **REL-02**: Verify duplicate webhook delivery is handled gracefully
- [ ] **REL-03**: Verify expired sessions are rejected

### 7.4 Input Validation Tests

- [ ] **VAL-01**: Verify oversized payload (>10MB) is rejected with 413
- [ ] **VAL-02**: Verify malformed JSON is rejected with 400
- [ ] **VAL-03**: Verify SQL injection attempts are escaped by ORM

______________________________________________________________________

## 8. Open Questions Resolution

| Question (from Architecture Brief)              | Resolution                                     |
| ----------------------------------------------- | ---------------------------------------------- |
| Webhook retry handling                          | Rely on GitHub retries; idempotent processing  |
| Real-time updates (polling vs SSE vs WebSocket) | Defer to Phase 2; polling acceptable for MVP   |
| Session refresh (sliding vs fixed)              | Sliding expiration (update `last_activity_at`) |
| Large payload storage                           | Inline JSONB; external storage if >1MB         |

______________________________________________________________________

## 9. Gate Checklist

- [x] Threat model has been evaluated
- [x] Abuse cases have been analyzed
- [x] NFR completeness has been checked (security, performance, reliability,
  observability)
- [x] Migration and rollback risks have been assessed
- [x] Every high-risk item has a mitigation and owner
- [x] Test requirements are defined for each risk category

______________________________________________________________________

## 10. Conclusion

**Gate Status: ✅ PASSED**

The Phase 1 architecture is approved for implementation. The design includes
appropriate security controls for a single-user MVP. Key strengths:

1. **Solid authentication**: GitHub OAuth + secure sessions
1. **Webhook integrity**: Mandatory HMAC-SHA256 verification
1. **Data isolation**: User-scoped access throughout
1. **Idempotency**: Delivery ID deduplication

High-priority recommendations (rate limiting, audit logging, connection pooling)
should be addressed early in implementation.

______________________________________________________________________

**Document generated by:** @risk-and-nfr-gate agent

**Next Steps:**

1. `@test-drafter` — Create failing tests based on test requirements above
1. `@implementation-driver` — Implement Phase 1 with TDD approach
1. `@ui-scaffolder` — Create SvelteKit UI scaffolds based on API contract
