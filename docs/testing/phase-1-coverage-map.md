# Phase 1 Test Coverage Map

**Agent:** @test-drafter

**Date:** January 18, 2026

**Phase:** TDD Red Phase (Failing Tests)

______________________________________________________________________

## checkpoint: agent: test-drafter stage: Testing status: in-progress created: 2026-01-18 next_agents: - agent: implementation-driver action: Make failing tests pass (TDD Green phase) - agent: test-truth-and-stability-gate action: Review tests for quality and determinism

______________________________________________________________________

## 1. Test Strategy

### Test Pyramid Distribution

| Layer             | Target % | Focus                                    |
| ----------------- | -------- | ---------------------------------------- |
| Unit Tests        | 60-70%   | Business logic, validators, utilities    |
| Integration Tests | 20-30%   | API endpoints, DB operations, OAuth flow |
| E2E Tests         | 5-10%    | Critical paths only (login → dashboard)  |

### Test Framework Stack

- **Python Backend**: pytest + pytest-asyncio + httpx (async client)
- **Mocking**: pytest-mock, respx (HTTP mocking)
- **Database**: SQLite in-memory for tests
- **Coverage**: pytest-cov (target: 80%+ for core modules)

______________________________________________________________________

## 2. Story-to-Test Mapping

### Story 0: User Authentication (OAuth Login)

| AC Scenario                                | Test Layer  | Test ID                             | Status   |
| ------------------------------------------ | ----------- | ----------------------------------- | -------- |
| Visit home page → redirect to login        | Integration | `test_unauthenticated_redirect`     | 🔴 Draft |
| Click "Login with GitHub" → OAuth redirect | Integration | `test_oauth_login_redirect`         | 🔴 Draft |
| OAuth callback success → session created   | Integration | `test_oauth_callback_success`       | 🔴 Draft |
| Session valid → dashboard access           | Integration | `test_authenticated_access`         | 🔴 Draft |
| Session expired → redirect to login        | Integration | `test_session_expired`              | 🔴 Draft |
| Logout → session destroyed                 | Integration | `test_logout_destroys_session`      | 🔴 Draft |
| OAuth callback error → error message       | Integration | `test_oauth_callback_error`         | 🔴 Draft |
| OAuth token exchange fails                 | Integration | `test_oauth_token_exchange_failure` | 🔴 Draft |
| Get user profile                           | Integration | `test_get_current_user`             | 🔴 Draft |

### Story 0b: App Installation & Repository Access

| AC Scenario                             | Test Layer  | Test ID                               | Status   |
| --------------------------------------- | ----------- | ------------------------------------- | -------- |
| No repos connected → empty state        | Integration | `test_no_installations_empty_state`   | 🔴 Draft |
| Install GitHub App → callback processed | Integration | `test_installation_callback`          | 🔴 Draft |
| Update repository selection             | Integration | `test_installation_update`            | 🔴 Draft |
| Suspend installation webhook            | Integration | `test_installation_suspended_webhook` | 🔴 Draft |
| Uninstall webhook                       | Integration | `test_installation_deleted_webhook`   | 🔴 Draft |
| Generate installation access token      | Unit        | `test_jwt_generation`                 | 🔴 Draft |
| Single installation constraint          | Integration | `test_single_installation_per_user`   | 🔴 Draft |

### Story 1: GitHub App Webhook Receiver

| AC Scenario                        | Test Layer  | Test ID                              | Status   |
| ---------------------------------- | ----------- | ------------------------------------ | -------- |
| Valid webhook → 200 OK             | Integration | `test_valid_webhook_accepted`        | 🔴 Draft |
| Invalid signature → 401            | Integration | `test_invalid_signature_rejected`    | 🔴 Draft |
| Missing signature → 401            | Integration | `test_missing_signature_rejected`    | 🔴 Draft |
| Duplicate delivery ID → idempotent | Integration | `test_duplicate_delivery_idempotent` | 🔴 Draft |
| Malformed JSON → 400               | Integration | `test_malformed_json_rejected`       | 🔴 Draft |
| Unconnected repo webhook → ignored | Integration | `test_unconnected_repo_ignored`      | 🔴 Draft |
| HMAC-SHA256 verification           | Unit        | `test_hmac_verification`             | 🔴 Draft |

### Story 2: Event Stream Storage

| AC Scenario                  | Test Layer  | Test ID                            | Status   |
| ---------------------------- | ----------- | ---------------------------------- | -------- |
| Store valid event            | Integration | `test_store_event`                 | 🔴 Draft |
| Store with GitHub timestamp  | Integration | `test_event_with_github_timestamp` | 🔴 Draft |
| Concurrent inserts (no race) | Integration | `test_concurrent_event_inserts`    | 🔴 Draft |
| Query by repository          | Integration | `test_query_events_by_repo`        | 🔴 Draft |
| Deduplication on insert      | Integration | `test_duplicate_event_rejected`    | 🔴 Draft |
| Query isolation by user      | Integration | `test_event_query_user_isolation`  | 🔴 Draft |
| Event pagination             | Integration | `test_event_pagination`            | 🔴 Draft |

______________________________________________________________________

## 3. Security Tests (from Risk Review)

| Test ID    | Requirement                              | Layer       | Status   |
| ---------- | ---------------------------------------- | ----------- | -------- |
| AUTH-01    | Unauthenticated → 401                    | Integration | 🔴 Draft |
| AUTH-02    | Secure cookie flags                      | Integration | 🔴 Draft |
| AUTH-03    | OAuth state validation                   | Integration | 🔴 Draft |
| AUTH-04    | CSRF token required                      | Integration | 🔴 Draft |
| WEBHOOK-01 | Invalid HMAC → 401                       | Integration | 🔴 Draft |
| WEBHOOK-02 | Missing signature → 401                  | Integration | 🔴 Draft |
| WEBHOOK-03 | Duplicate delivery rejected              | Integration | 🔴 Draft |
| AUTHZ-01   | Cannot access other user's installations | Integration | 🔴 Draft |
| AUTHZ-02   | Cannot access other user's events        | Integration | 🔴 Draft |

______________________________________________________________________

## 4. Performance Tests

| Test ID | Requirement                | Target                  | Status      |
| ------- | -------------------------- | ----------------------- | ----------- |
| PERF-01 | Webhook processing latency | \<500ms p95             | 🟡 Deferred |
| PERF-02 | Dashboard API response     | \<3s with 50 repos      | 🟡 Deferred |
| PERF-03 | Event list query           | \<500ms for 1000 events | 🟡 Deferred |

______________________________________________________________________

## 5. Reliability Tests

| Test ID | Requirement                     | Layer       | Status   |
| ------- | ------------------------------- | ----------- | -------- |
| REL-01  | Health check → 503 when DB down | Integration | 🔴 Draft |
| REL-02  | Duplicate webhook handled       | Integration | 🔴 Draft |
| REL-03  | Expired session rejected        | Integration | 🔴 Draft |

______________________________________________________________________

## 6. Input Validation Tests

| Test ID | Requirement             | Layer       | Status   |
| ------- | ----------------------- | ----------- | -------- |
| VAL-01  | Oversized payload → 413 | Integration | 🔴 Draft |
| VAL-02  | Malformed JSON → 400    | Integration | 🔴 Draft |
| VAL-03  | SQL injection escaped   | Integration | 🔴 Draft |

______________________________________________________________________

## 7. Test File Structure

```
src/backend/
├── pyproject.toml           # Test dependencies
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures, test database, mocks
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_crypto.py   # HMAC, JWT, token hashing
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth.py     # OAuth flow, sessions
│   │   ├── test_installations.py
│   │   ├── test_webhooks.py
│   │   ├── test_events.py
│   │   └── test_health.py
│   └── fixtures/
│       ├── __init__.py
│       ├── users.py
│       ├── installations.py
│       ├── webhooks.py
│       └── events.py
```

______________________________________________________________________

## 8. Implementation Priority

### Batch 1: Core Infrastructure (Story 0, 1)

1. Auth tests (OAuth flow, sessions)
1. Webhook verification tests (HMAC)
1. Health check tests

### Batch 2: Data Layer (Story 0b, 2)

4. Installation tests
1. Event storage tests

### Batch 3: Security & NFR

6. Security tests (AUTH-*, AUTHZ-*)
1. Input validation tests

______________________________________________________________________

## 9. Next Steps

After tests are drafted:

1. Run tests → verify they FAIL (Red phase ✅)
1. Hand off to `@implementation-driver` for Green phase
1. Return for additional edge cases after implementation

______________________________________________________________________

**Document generated by:** @test-drafter agent

**Related documents:**

- [Phase 1 User Stories](../phase-1-user-stories.md)
- [Risk & NFR Review](../architecture/phase-1-risk-nfr-review.md)
- [API Contract](../architecture/phase-1-api-contract.md)
