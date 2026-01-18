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

#### Backend (Python)

- **Framework**: pytest + pytest-asyncio + httpx (async client)
- **Mocking**: pytest-mock, respx (HTTP mocking)
- **Database**: SQLite in-memory for tests
- **Coverage**: pytest-cov (target: 80%+ for core modules)

#### Frontend (SvelteKit 2.x)

- **Unit/Component**: Vitest + @testing-library/svelte
- **E2E**: Playwright (cross-browser)
- **Component Library**: shadcn-svelte (accessible components)
- **Coverage**: @vitest/coverage-v8 (target: 80%+ for components)
- **Package Manager**: pnpm

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

### Backend (Python)

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

### Frontend (SvelteKit 2.x)

```
src/frontend/
├── package.json             # pnpm dependencies
├── vitest.config.ts         # Vitest configuration
├── playwright.config.ts     # Playwright configuration
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── __tests__/   # Component unit tests
│   │   │   │   ├── EventCard.test.ts
│   │   │   │   ├── EventList.test.ts
│   │   │   │   ├── RepositoryCard.test.ts
│   │   │   │   ├── Dashboard.test.ts
│   │   │   │   └── LoginButton.test.ts
│   │   │   └── ui/          # shadcn-svelte components
│   │   └── stores/
│   │       └── __tests__/   # Store unit tests
│   │           └── auth.test.ts
│   └── routes/
│       └── __tests__/       # Route-level tests
├── tests/
│   └── e2e/                 # Playwright E2E tests
│       ├── login.spec.ts
│       ├── dashboard.spec.ts
│       ├── events.spec.ts
│       └── repositories.spec.ts
```

______________________________________________________________________

## 8. Frontend Test Cases

### Story 3: Repository Selection UI

| AC Scenario                     | Test Layer   | Test ID                       | Status   |
| ------------------------------- | ------------ | ----------------------------- | -------- |
| View connected repositories     | Component    | `RepositoryList.renders`      | 🔴 Draft |
| Search repositories             | Component    | `RepositoryList.filters`      | 🔴 Draft |
| Repository health indicator     | Component    | `RepositoryCard.healthBadge`  | 🔴 Draft |
| Empty state (no repos)          | Component    | `RepositoryList.emptyState`   | 🔴 Draft |
| Navigate to repository detail   | E2E          | `repositories.navigation`     | 🔴 Draft |
| GitHub API error handling       | Component    | `RepositoryList.errorState`   | 🔴 Draft |

### Story 4: Event Stream Viewer

| AC Scenario                     | Test Layer   | Test ID                       | Status   |
| ------------------------------- | ------------ | ----------------------------- | -------- |
| View recent events              | Component    | `EventList.renders`           | 🔴 Draft |
| Event card displays all fields  | Component    | `EventCard.displaysFields`    | 🔴 Draft |
| Filter events by type           | Component    | `EventList.filterByType`      | 🔴 Draft |
| Filter events by date range     | Component    | `EventList.filterByDate`      | 🔴 Draft |
| View raw payload                | Component    | `EventCard.rawPayload`        | 🔴 Draft |
| Pagination works                | E2E          | `events.pagination`           | 🔴 Draft |
| Empty state (no events)         | Component    | `EventList.emptyState`        | 🔴 Draft |
| Search events                   | Component    | `EventList.search`            | 🔴 Draft |

### Story 5: Minimal Dashboard

| AC Scenario                     | Test Layer   | Test ID                       | Status   |
| ------------------------------- | ------------ | ----------------------------- | -------- |
| Dashboard renders repos         | Component    | `Dashboard.rendersRepos`      | 🔴 Draft |
| Dashboard shows active issue    | Component    | `Dashboard.activeIssue`       | 🔴 Draft |
| Dashboard shows active PR       | Component    | `Dashboard.activePR`          | 🔴 Draft |
| Dashboard shows queue depth     | Component    | `Dashboard.queueDepth`        | 🔴 Draft |
| Health indicators               | Component    | `Dashboard.healthIndicators`  | 🔴 Draft |
| Navigate to repo detail         | E2E          | `dashboard.navigation`        | 🔴 Draft |
| Empty dashboard                 | Component    | `Dashboard.emptyState`        | 🔴 Draft |
| Auto-refresh works              | E2E          | `dashboard.autoRefresh`       | 🔴 Draft |

### Story 0: Login UI

| AC Scenario                     | Test Layer   | Test ID                       | Status   |
| ------------------------------- | ------------ | ----------------------------- | -------- |
| Login page renders              | Component    | `LoginPage.renders`           | 🔴 Draft |
| Login button redirects          | E2E          | `login.oauthRedirect`         | 🔴 Draft |
| Session expired message         | Component    | `LoginPage.sessionExpired`    | 🔴 Draft |
| Logout success message          | Component    | `LoginPage.logoutSuccess`     | 🔴 Draft |
| User menu shows profile         | Component    | `UserMenu.profile`            | 🔴 Draft |
| Full login → dashboard flow     | E2E          | `login.fullFlow`              | 🔴 Draft |

______________________________________________________________________

## 9. Frontend Accessibility Tests

| Test ID    | Requirement                              | Layer       | Status   |
| ---------- | ---------------------------------------- | ----------- | -------- |
| A11Y-01    | Keyboard navigation (all pages)          | E2E         | 🔴 Draft |
| A11Y-02    | Focus management on route change         | E2E         | 🔴 Draft |
| A11Y-03    | ARIA labels on interactive elements      | Component   | 🔴 Draft |
| A11Y-04    | Color contrast (WCAG AA)                 | E2E         | 🔴 Draft |
| A11Y-05    | Screen reader announcements              | E2E         | 🔴 Draft |

______________________________________________________________________

## 10. Implementation Priority

### Backend Batch 1: Core Infrastructure (Story 0, 1)

1. Auth tests (OAuth flow, sessions)
1. Webhook verification tests (HMAC)
1. Health check tests

### Backend Batch 2: Data Layer (Story 0b, 2)

4. Installation tests
1. Event storage tests

### Backend Batch 3: Security & NFR

6. Security tests (AUTH-*, AUTHZ-*)
1. Input validation tests

### Frontend Batch 1: Foundation (Story 0)

8. Login page component tests
1. User menu component tests
1. Auth store tests

### Frontend Batch 2: Core UI (Stories 3, 4)

11. Repository list/card component tests
1. Event list/card component tests
1. Navigation E2E tests

### Frontend Batch 3: Dashboard (Story 5)

14. Dashboard component tests
1. Auto-refresh E2E tests

### Frontend Batch 4: Accessibility

16. Keyboard navigation E2E tests
1. ARIA compliance tests

______________________________________________________________________

## 11. Next Steps

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
