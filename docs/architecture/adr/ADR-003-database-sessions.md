# ADR-003: Database-Backed Sessions

**Status:** Accepted

**Date:** January 18, 2026

**Deciders:** @arch-spec-author, @requirements

______________________________________________________________________

## Context

The application requires user sessions for authentication. Sessions must:

- Persist across server restarts
- Support session expiration (30 days)
- Allow session lookup by token
- Enable session invalidation (logout)
- Scale to multiple backend instances (if needed)

______________________________________________________________________

## Decision

We will use **database-backed sessions** stored in a `user_sessions` table,
using SQLModel with the same PostgreSQL/SQLite database as other application
data.

______________________________________________________________________

## Options Considered

### Option A: Database Sessions (Selected)

**Storage:** PostgreSQL/SQLite `user_sessions` table

**Pros:**

- Consistent with existing data layer
- No additional infrastructure
- Easy to query (active sessions, cleanup)
- Transactional consistency with user data
- Works with SQLite for development

**Cons:**

- Slightly slower than in-memory stores
- Database load for every authenticated request
- Must implement session cleanup (cron or on-access)

### Option B: Redis Sessions

**Storage:** Redis key-value store

**Pros:**

- Very fast (in-memory)
- Native TTL (automatic expiration)
- Scales well for high traffic

**Cons:**

- Additional infrastructure (Redis server)
- Network latency between backend and Redis
- Data loss risk if Redis not persisted
- Overkill for Phase 1 user count

### Option C: JWT Tokens (Stateless)

**Storage:** Token contains all session data (signed, not stored)

**Pros:**

- No server-side storage
- Scales infinitely (stateless)
- Fast validation (cryptographic)

**Cons:**

- Cannot revoke tokens (until expiry)
- Logout requires blocklist (defeats stateless)
- Token size grows with claims
- Refresh token complexity

### Option D: Signed Cookies (Server-side encryption)

**Storage:** Encrypted session data in cookie

**Pros:**

- Stateless (no server storage)
- Simple implementation

**Cons:**

- Cookie size limits
- Cannot easily revoke
- Session data in every request

______________________________________________________________________

## Consequences

### Positive

- Simple architecture (one database)
- Easy session management (list, revoke, cleanup)
- Development parity (SQLite works same as PostgreSQL)
- Can migrate to Redis later without API changes

### Negative

- Database query on every authenticated request
- Must implement periodic session cleanup

### Mitigations

- Index on `session_token` for fast lookup
- Index on `expires_at` for cleanup queries
- Connection pooling reduces connection overhead
- Session token is hashed (not plaintext in DB)

### Session Cleanup Strategy

```python
# Cleanup expired sessions (run periodically or on-demand)
async def cleanup_expired_sessions():
    await session.exec(
        delete(UserSession).where(UserSession.expires_at < datetime.utcnow())
    )
```

Options:

1. Background task on application startup
1. Cleanup on each session validation (probabilistic)
1. Scheduled job (cron or APScheduler)

______________________________________________________________________

## Implementation Notes

### Session Token Generation

```python
import secrets

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)  # 256 bits of entropy
```

### Session Token Storage

```python
import hashlib

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

### Cookie Settings

```python
response.set_cookie(
    key="session",
    value=session_token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="lax",
    max_age=30 * 24 * 60 * 60,  # 30 days
)
```

______________________________________________________________________

## Related Documents

- [Phase 1 Data Model](../phase-1-data-model.md)
- [ADR-001: FastAPI + SQLModel](./ADR-001-fastapi-sqlmodel.md)

______________________________________________________________________

**Decision recorded by:** @arch-spec-author agent
