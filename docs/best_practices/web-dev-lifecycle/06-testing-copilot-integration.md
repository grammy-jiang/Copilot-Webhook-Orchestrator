# Testing Stage: Copilot Drafts Tests; You Guarantee Truthfulness, Stability, and Critical Coverage (Practical + Repeatable)

Copilot can **accelerate test production**, but it will also happily generate
**low-signal tests** (over-mocked, brittle selectors, meaningless assertions)
unless you impose **hard gates**. Your operating model should be: **AI drafts →
you validate intent/coverage → CI enforces discipline**.

______________________________________________________________________

## A. Baseline setup (so Copilot can’t generate junk tests)

### 1) Repo instructions = “test policy”

- Put cross-repo rules in `.github/copilot-instructions.md` and test-specific
  rules via `.github/instructions/*.instructions.md` with `applyTo` (e.g.,
  `**/*test*`, `tests/**`, `e2e/**`).
- Define agent governance in `AGENTS.md` (what the test agent may touch; what
  requires human approval).
- Use prompt files under `.github/prompts/` to standardize test-generation tasks
  and invoke them via `/...` in supported IDEs.

**Non-negotiables to encode**

- **No fake assertions**: every test must assert user-visible or
  contract-visible behavior.
- **No snapshot spam**: snapshots only for stable, reviewed UI surfaces.
- **No brittle selectors** in E2E: prefer user-facing locators; use explicit
  test IDs when needed.
- **Determinism required**: fixed clocks, seeded randomness, hermetic fixtures,
  stable test data.
- **Layer discipline**: unit tests for logic, integration for boundaries, E2E
  for critical paths only.

### 2) Copilot interaction rules = “use the right command”

- Use Copilot Chat test drafting as scaffolding only. Treat generated tests as a
  first draft that requires validation.

### 3) Test Pyramid Strategy (Default)

Follow the **test pyramid** from TDD best practices:

```
        /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
       /   E2E (Few, Slow)      \
      /    Critical paths only   \
     /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
    /   Integration (Some)        \
   /    Module boundaries, APIs    \
  /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
 /      Unit Tests (Many, Fast)       \
/    Business logic, utilities         \
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
```

**Distribution guidance:**

- **Unit tests**: many (fast, stable, cheap) — core modules target ≥95% coverage
- **Smoke tests**: fast "gate" checks in CI — verify critical paths
- **E2E tests**: few (slow, highest maintenance) — if E2E explodes in quantity,
  it's a design/testability problem

______________________________________________________________________

## B. Test strategy with Copilot embedded (end-to-end)

### 1) Test plan intake → “coverage map”

**Goal:** force test intent before test code.

**You provide**

- story/spec acceptance criteria + edge cases
- risk hotspots (auth, billing, permission, concurrency, migrations)
- “critical path” definition (what must never break)

**Copilot outputs**

- a coverage map: **Unit / Integration / Contract / E2E** per story slice
- explicit “won’t test here” decisions (keeps the suite sane)

**Gate:** if a test can’t be tied to an acceptance criterion or risk item, it’s
noise.

______________________________________________________________________

### 2) Unit tests (fast truth) → “behavioral assertions”

**Copilot does**

- drafts test cases + fixtures + mocks
- enumerates edge conditions (null/empty, invalid types, boundaries)

**You must enforce**

- test the **business rule**, not the implementation detail
- avoid over-mocking internal functions (mock boundaries, not the whole world)

______________________________________________________________________

### 3) Integration/contract tests (boundary truth) → “contracts don’t drift”

**Copilot does**

- drafts API contract tests (status codes, error model, pagination, validation)
- drafts DB-integration tests (migrations, queries, constraints, indexes)

**You must enforce**

- realistic data shapes (mirror production payload constraints)
- stable test isolation (clean DB, seeded fixtures, transaction rollback)

______________________________________________________________________

### 4) E2E tests (critical-path only) → “stability engineering”

This is where most teams bleed time. Your job is to keep E2E **small and
resilient**.

**Copilot does**

- drafts Playwright/Cypress scripts for top user flows
- drafts test data setup and teardown steps

**You must enforce stability practices**

- Use robust locators (prefer user-facing attributes; avoid DOM-structure
  coupling).
- When necessary, define explicit test IDs and use `getByTestId`.
- Avoid long CSS/XPath chains that bind to DOM structure (classic flake
  generator).

______________________________________________________________________

### 5) Flake handling and debuggability → “traces as a first-class artifact”

**Copilot does**

- suggests retries, timeouts, and tracing configurations

**You must enforce**

- “retry is a band-aid, not a cure” — root-cause flaky tests
- enable actionable diagnostics in CI (traces/logs/screenshots as appropriate)

______________________________________________________________________

### 6) Live browser testing with MCP → "real browser validation"

**Goal:** verify UX behavior and frontend-backend integration in a real browser.

Use **browser MCP tools** (Playwright, Chrome, Firefox) for live testing:

**UX Behavior Testing:**

- user flows work end-to-end in real browser
- interactions (click, type, hover, drag) work correctly
- visual feedback (spinners, alerts, toasts) appears as expected
- navigation and routing work across the app
- responsive behavior at different viewport sizes

**Frontend-Backend Integration Testing:**

- API requests are made to correct endpoints
- request payloads match the API contract
- UI updates correctly with API responses
- error scenarios (network errors, 4xx, 5xx) handled gracefully
- authentication flow works (login, logout, session handling)

**Live testing workflow:**

```typescript
// Capture network requests to verify backend communication
const [request] = await Promise.all([
  page.waitForRequest('/api/users'),
  page.getByRole('button', { name: 'Load Users' }).click(),
]);
expect(request.method()).toBe('GET');

// Verify response is rendered
await expect(page.getByTestId('user-count')).toHaveText('10 users');

// Test error handling
await page.route('/api/data', route => route.abort());
await page.getByRole('button', { name: 'Fetch Data' }).click();
await expect(page.getByText('Network error')).toBeVisible();

// Verify form submission
const [submitRequest] = await Promise.all([
  page.waitForRequest('/api/submit'),
  page.getByRole('button', { name: 'Submit' }).click(),
]);
expect(submitRequest.postDataJSON()).toMatchObject({ email: 'user@example.com' });
```

**Browser DevTools integration:**

- **Network panel**: Inspect API calls, headers, payloads, timing
- **Console**: Check for JavaScript errors during test runs
- **Accessibility panel**: Verify computed ARIA names and roles

**Gate:** before E2E tests are committed, verify they pass in a real browser
using MCP tools.

______________________________________________________________________

## C. CI enforcement (the quality floor you don’t negotiate)

- Use branch protection/rulesets to require **status checks** before merge and
  enforce “PR-only” merges.
- Make test failures blocking. If CI doesn’t block it, it will slip.

### CI Quality Gates (from TDD Best Practices)

**Pipeline phases (recommended order):**

1. **Format + Lint** (fast fail)
1. **Unit tests** (high coverage)
1. **Smoke tests** (quick system sanity)
1. **E2E tests** (critical journeys; slower; strong artifacts)

**Quality gate defaults:**

- Core modules coverage target: **≥95%** where justified
- **No flaky tests** tolerated in mainline
- PR merge blocked on failures in phases 1–3
- E2E may be required for protected branches/releases depending on risk
  tolerance

**Flake policy:**

- Treat flaky tests as **defects**: isolate → fix root cause → restore to main
  pipeline
- Avoid masking with retries; use retries only as temporary mitigation with
  tracking

**Reporting requirements:**

- Publish junit/xml or equivalent test reports
- Publish coverage reports
- Publish E2E artifacts (screenshots/traces on failure)
- Make failures actionable: logs + minimal reproduction steps

______________________________________________________________________

## D. Recommended custom agents for Testing (pragmatic set)

Keep the same pattern you’ve been using: **one builder agent + one gate agent**.

### 1) `test-drafter.agent.md` (primary agent)

**Mission:** draft tests quickly at the correct layer with realistic data and
meaningful assertions.

**Non-negotiables**

- map each test to an AC/risk item
- choose the smallest effective layer (unit > integration > E2E)
- deterministic fixtures (seeded, isolated)
- no brittle selectors; prefer roles/test IDs for E2E
- no weakening checks to “make CI green”

### 2) `test-truth-and-stability-gate.agent.md` (gate agent)

**Mission:** aggressively reject low-signal or flaky tests and demand evidence.

**Non-negotiables**

- reject assertion-less tests and over-mocked tests
- enforce E2E locator discipline and state isolation
- require CI artifacts for failures (trace/logs)
- require critical-path coverage for high-risk stories

### Optional specialist agents (only if pain exists)

- `e2e-stabilizer` — locator strategy + flake triage + trace-first debugging
- `contract-test-author` — API schema/error model tests
- `coverage-analyst` — coverage reports + “coverage that matters” guidance

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store under `.github/prompts/` and invoke via `/...`:

- `/test-plan-from-story` → coverage map by layer + risk hotspots
- `/unit-tests-from-code` → fast unit tests with real assertions
- `/integration-tests-for-boundary` → DB/API integration tests + setup/teardown
- `/contract-tests-from-openapi` → status/error/validation/pagination contract
  tests
- `/e2e-tests-critical-path` → Playwright flows with stable locator rules
- `/flake-triage-with-trace` → root-cause flake plan + diagnostics suggestions

______________________________________________________________________

## Example prompt file skeleton (E2E stability-first)

```markdown
---
name: e2e-tests-critical-path
description: Draft E2E tests for critical paths with stability rules
agent: test-drafter
tools: [workspace]
---

Input:
1) ${input:story:Paste story + acceptance criteria}
2) ${input:flows:List the 1–3 critical flows}

Rules:
- Only critical paths. Keep the suite small.
- Prefer user-facing locators (role/text). Use getByTestId only when needed.
- Avoid long CSS/XPath chains.
- Add deterministic test data setup/teardown.
- Include failure-state assertions (auth, validation, empty, network error).

Deliverables:
- E2E tests + helpers
- test data fixtures
- notes: assumptions + open questions
```

______________________________________________________________________

## Next step suggestion

The following artifacts are now available in this repository:

- `.github/agents/test-drafter.agent.md` ✅
- `.github/agents/test-truth-and-stability-gate.agent.md` ✅
- `.github/copilot-instructions.md` ✅ With TDD and test standards

### Issue Template for Testing Stage

| Template               | Use When              | Key Fields                                                       |
| ---------------------- | --------------------- | ---------------------------------------------------------------- |
| `06-test-case-gap.yml` | Missing test coverage | Related Story, Untested AC, Proposed Tests, Determinism Concerns |
