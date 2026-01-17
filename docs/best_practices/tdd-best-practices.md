# Test-Driven Development (TDD) Best Practices

This document is a **best-practice, tool-oriented TDD guide** designed to be
easy for both humans and AI coding assistants (GitHub Copilot, Claude Code,
ChatGPT Codex) to follow. It is intentionally **principle-driven + schematic**,
with **no real-world samples**.

______________________________________________________________________

## 1. What “TDD” Means in Practice

**TDD loop: Red → Green → Refactor**

1. **Red**: Write a test for the next small behavior. Run it and confirm it
   fails for the right reason.
1. **Green**: Implement the smallest change that makes the new test pass.
1. **Refactor**: Improve structure (remove duplication, clarify naming, improve
   design) while keeping all tests green.

**Non-negotiables**

- One failing test at a time.
- Small increments, frequent runs.
- Refactor is part of the cycle, not optional.

______________________________________________________________________

## 2. Global Quality Principles (All Languages)

### 2.1 Test Design Rules

- **Behavior over implementation**: verify *what* the system does, not *how* it
  does it internally.
- **Single responsibility per test**: one behavior/branch per test.
- **Deterministic**: no reliance on time, random, external network, shared
  mutable state.
- **Readable**: use clear names, consistent structure, and minimal “logic”
  inside tests.
- **Independent**: tests can run in any order; no hidden coupling.

### 2.2 Standard Test Structure

Use **AAA** in every test:

- **Arrange**: setup inputs, dependencies, and state
- **Act**: call the unit / route / UI action
- **Assert**: validate outputs and relevant side-effects

### 2.3 Test Pyramid (Default Strategy)

- **Many unit tests** (fast, stable, cheap)
- **Some smoke tests** (fast critical-path checks)
- **Few end-to-end tests** (slow, highest maintenance cost)

If E2E explodes in quantity, it’s usually a **design/testability** problem.

______________________________________________________________________

## 3. Test Types You Use: Definitions + Expectations

### 3.1 Unit Tests

**Scope**: a function/class/module in isolation **Properties**

- Fast (milliseconds)
- No real network or external services
- Use mocks/stubs/fakes at boundaries
- Highest coverage (core modules can target ≥95%)

### 3.2 Smoke Tests

**Scope**: minimal “system is alive” checks **Properties**

- Fast “gate” tests in CI
- Verify start-up/health endpoints, core dependency wiring, key route works
- Minimal assertions; detect catastrophic breakages early

### 3.3 End-to-End (E2E) Tests

**Scope**: user-visible flows across components (UI/API/DB) **Properties**

- Slowest, highest maintenance
- Focus on critical journeys only
- Must be reproducible: controlled test data, resettable state, strong
  diagnostics (logs/screenshots/traces)

______________________________________________________________________

# Part A — Python (unittest, mock, pytest, tox)

## A1. Default Tooling and Roles

- **pytest**: default test runner for most projects (fixtures, parametrization,
  plugins)
- **unittest**: acceptable for legacy or when class-based organization is
  required
- **unittest.mock**: standard mocking; use `patch`, `Mock`, `MagicMock`,
  autospeccing where appropriate
- **tox**: orchestrate consistent environments and test commands across Python
  versions and dependency sets

## A2. Repository Structure (Recommended)

```
repo/
  src/                    # or your package root
  tests/
    unit/
    smoke/
    e2e/
  pyproject.toml          # or setup.cfg
  tox.ini
```

**Naming**

- test files: `test_*.py`
- test functions: `test_<condition>_<expected_behavior>`
- prefer explicit names over generic (`test_ok`, `test1`)

## A3. Unit Tests in Python — Best Practices

### A3.1 Isolation Strategy

- Mock external boundaries:
  - HTTP calls, DB clients, message queues, filesystem, system clock, randomness
- Do **not** mock deep internal calls unless the call itself is the contract.
- Prefer injecting dependencies (constructor args, function params) over
  hard-coded globals.

### A3.2 Mocking Rules (unittest.mock)

- **Mock boundaries, not internals**: avoid verifying private method calls
  unless required.
- Avoid “over-specified” tests:
  - Don’t assert exact call counts/order unless the behavior requires it.
- Prefer `spec` / `autospec` for safer mocks (catch wrong attribute/method
  usage).
- Make failures explainable:
  - Keep mock setups minimal and aligned with test intent.

### A3.3 pytest Fixtures

- Put shared fixtures into `conftest.py`.
- Use meaningful fixture names (business semantics).
- Default `scope="function"` for isolation; increase scope only when you control
  shared state.

### A3.4 Parametrization

- Use parametrized tests instead of loops inside a single test.
- Keep each parameter set meaningful; avoid “test matrices” that hide intent.

### A3.5 Assertions

- Assert the minimum required to prove the behavior.
- Avoid asserting incidental details (internal formatting, private state) unless
  part of contract.

## A4. Smoke Tests in Python — Best Practices

### A4.1 What to Verify

- Service starts
- Health endpoint responds
- Critical route(s) return expected status + basic shape

### A4.2 What NOT to Do

- No deep data assertions
- No heavy fixtures
- No “full-system correctness” checks (that’s E2E/integration)

## A5. E2E Tests in Python/Full Stack — Best Practices

### A5.1 Environment Discipline

- Dedicated test environment (containers or isolated services)
- Resettable DB state (seed + cleanup)
- Deterministic test data

### A5.2 Diagnostics Are Mandatory

- Capture:
  - server logs
  - request/response traces
  - screenshots/videos (if UI involved)
  - test artifacts (reports, coverage where relevant)

### A5.3 Flake Policy

- Treat flaky tests as defects:
  - isolate → fix root cause → restore to main pipeline
- Avoid masking with retries; use retries only as temporary mitigation with
  tracking.

## A6. tox — Environment and Command Orchestration

### A6.1 Goals

- Single entry point for:
  - lint
  - unit
  - smoke
  - e2e
- Ensure “works on my machine” becomes “works in reproducible envs”.

### A6.2 Good tox Practices

- Separate envs by concern (`py311-unit`, `py311-smoke`, `py311-e2e`, `lint`)
- Pin or constrain dependencies appropriately for reproducibility
- In CI:
  - PR: lint + unit + smoke
  - nightly/release: add e2e and multi-Python matrix

______________________________________________________________________

# Part B — JavaScript/TypeScript (Unit, Smoke, E2E + Headless Browser)

## B1. Recommended Default Stack

- **Unit/Smoke**: **Jest** (or **Vitest** for Vite-based stacks)
- **UI behavior tests**: **Testing Library** (React Testing Library, etc.)
- **E2E / headless browser**: **Playwright** (default recommendation), or
  Cypress

Rationale: Playwright is strong for **headless browser user interaction**,
cross-browser support, and CI-friendly diagnostics.

## B2. Repository Structure (Recommended)

```
repo/
  src/
  tests/
    unit/
    smoke/
    e2e/
  package.json
  tsconfig.json
  playwright.config.ts      # if using Playwright
```

**Naming**

- test files: `*.test.ts` / `*.spec.ts`
- test names: include condition + expected result (e.g., “should show error when
  …”)

## B3. Unit Tests in JS/TS — Best Practices

### B3.1 Isolation and Mocking

- Mock external boundaries:
  - network calls (fetch/axios), timers, randomness, storage, analytics
- Prefer mocking at module boundaries, not inside component internals.
- Avoid over-asserting call sequences unless contractually required.

### B3.2 UI Component Tests (Testing Library Principles)

- Test the UI as a user would:
  - what renders
  - what is clickable
  - what messages appear
- Avoid asserting implementation details:
  - internal state
  - component tree structure
  - CSS class names (unless contract)

## B4. Smoke Tests in JS/TS — Best Practices

- Build succeeds
- App boots
- One or two critical routes render without fatal error
- For full stack: verify a minimal request path end-to-end with minimal asserts

## B5. E2E with Headless Browser (Playwright) — Best Practices

### B5.1 Focus: Critical Journeys Only

- Login, onboarding, checkout, core workflows
- Keep the suite small and meaningful.

### B5.2 Selector Strategy (Stability First)

- Use stable selectors:
  - `data-testid`, `data-e2e`, etc.
- Avoid brittle selectors:
  - deeply nested CSS selectors
  - text that frequently changes
  - layout-dependent selectors

### B5.3 Deterministic Data and State

- Reset state per test or per suite (DB reset, seeded accounts, isolated
  tenants)
- Avoid dependence on real production-like drifting data.

### B5.4 Diagnostics and Artifacts

- Always enable:
  - screenshots on failure
  - traces
  - console/network logs
  - optional video for flaky investigations

### B5.5 Anti-Flake Rules

- Prefer “wait for condition/event” over `sleep`.
- Fix root cause (race conditions, unstable selectors, non-deterministic state).
- Quarantine failing E2E tests if needed, but track and resolve quickly.

______________________________________________________________________

## 4. CI/CD Integration Blueprint (Language-Agnostic)

### 4.1 Pipeline Phases (Recommended)

1. **Format + Lint** (fast fail)
1. **Unit** (high coverage)
1. **Smoke** (quick system sanity)
1. **E2E** (critical journeys; slower; strong artifacts)

### 4.2 Quality Gates (Suggested Defaults)

- Core modules coverage target (e.g., ≥95% where justified)
- No flaky tests tolerated in mainline
- PR merge blocked on failures in phases 1–3; E2E may be required for protected
  branches/releases depending on risk tolerance

### 4.3 Reporting

- Publish:
  - junit/xml or equivalent test reports
  - coverage reports
  - E2E artifacts (screenshots/traces)
- Make failures actionable: logs + minimal reproduction steps.

______________________________________________________________________

## 5. AI-Friendly “Rules of Engagement” (Use This to Guide Codegen)

When generating or modifying code:

- Add/adjust tests **first** for new behavior.
- Keep tests:
  - small
  - behavior-focused
  - deterministic
- Use the project’s directory and naming conventions.
- Mock only at boundaries and keep mocks minimal.
- Update CI commands if introducing new test categories or tools.
- Prefer removing flakiness at the root cause instead of adding retries.

______________________________________________________________________

## 6. Quick Checklists

### Python Unit Test Checklist

- [ ] AAA structure
- [ ] No external I/O
- [ ] Mocks at boundaries only
- [ ] Clear test name: condition + expected outcome
- [ ] Minimal assertions proving behavior

### Smoke Test Checklist

- [ ] Fast
- [ ] Critical path only
- [ ] Minimal asserts
- [ ] Runs early in CI

### E2E Checklist

- [ ] Stable selectors (`data-*`)
- [ ] Deterministic data/state
- [ ] Strong diagnostics enabled
- [ ] Small suite covering critical journeys
- [ ] No arbitrary sleeps; wait for conditions
