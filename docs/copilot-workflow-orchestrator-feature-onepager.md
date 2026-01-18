# Copilot Workflow Orchestrator — Feature One-Pager

**Status:** Requirements Phase Complete

**Date:** January 17, 2026

**Agent:** @requirements

______________________________________________________________________

## Problem Statement

GitHub Copilot Coding Agent automates implementation work, but developers are
still stuck performing **repetitive manual GitHub workflow tasks**:

- Manually assigning next issues to Copilot after PR merges
- Manually requesting Copilot code reviews
- Manually prompting Copilot to fix review comments
- Manually tracking issue/PR state across multiple repositories
- No visibility into the webhook event stream or automation status

This creates **workflow friction**, **delays between issues**, and **high
cognitive load** for developers managing multiple repositories.

______________________________________________________________________

## Proposed Solution

**Copilot Workflow Orchestrator** - A webhook-driven automation service that:

1. **Listens to GitHub webhooks** (issues, PRs, reviews, CI checks)
1. **Maintains a state machine** per repository (queued -> in_progress -> review
   -> merge -> next)
1. **Executes automated actions**:
   - Auto-assign next queued issue to Copilot after PR merge
   - Auto-request Copilot to fix review comments with customizable prompts
   - Auto-post CI failure remediation requests
   - Auto-label issues/PRs for state tracking
1. **Provides visibility**: Event stream viewer + minimal dashboard per repo
1. **Enforces single concurrency**: 1 active issue per repo at a time
1. **Fails closed**: Ambiguous states -> `needs_human` + notification

______________________________________________________________________

## Success Metrics

### Efficiency Gains

- **≥80% reduction in manual GitHub actions** per issue lifecycle (baseline: ~8
  manual steps → target: \<2)
- **≤2 minutes delay** between PR merge and next issue assignment (baseline:
  manual = hours/days)
- **100% issue-to-PR traceability** with automated state labels

### Quality & Reliability

- **Zero missed webhook events** (idempotent processing + delivery verification)
- **100% audit trail** (every automated action logged with context)
- **≥99% uptime** for webhook receiver

### Operational

- **Manage ≤10 repositories** concurrently in MVP (scale target: 50+)
- **1-year event retention** with pagination/filtering
- **≤5 seconds** dashboard load time

______________________________________________________________________

## Constraints

### Technical

- **Backend:** FastAPI (Python) with SQLModel ORM
- **Frontend:** SvelteKit 2.x (Svelte 5) with Tailwind CSS
- **UI Components:** shadcn-svelte (accessible, Tailwind-based)
- **Database:** PostgreSQL (production) / SQLite (development)
- **Package Management:**
  - Backend: `uv` for Python virtual environment and dependencies
  - Frontend: `pnpm` for Node.js package management
- **Frontend Testing:**
  - Unit/Component: Vitest + @testing-library/svelte
  - E2E: Playwright
- **Deployment:** Docker-based (full stack: backend + frontend + DB)
- **Serverless-compatible:** (platform TBD, must support Python)

### Scope

- **Single-org/single-tenant MVP** (multi-tenant deferred to Phase 6+)
- **Webhook event volume:** ~3 events/minute per repo (10 repos = 30 events/min
  = 43K events/day)
- **No code diff analysis:** AI/automation operates on workflow metadata only

### Security

- GitHub App (not PAT) with least-privilege permissions
- Webhook signature verification mandatory
- Secrets in managed vault (not code)
- RBAC (Owner/Admin/Viewer roles)

### Governance

- Fail-closed on ambiguity (default to `needs_human`)
- Human approval required for high-risk actions (merge, config changes)
- Phase 1-3: Core automation; Phase 5+: AI assist

______________________________________________________________________

## Out of Scope (Explicit)

- ❌ Modifying or analyzing source code diffs
- ❌ Editing GitHub Actions workflows (treated as code)
- ❌ Fully autonomous merging without human gate (Phase 1-4)
- ❌ Multi-installation support (deferred to Phase 6+)
- ❌ Real-time collaboration/chat features
- ❌ Custom Copilot agent definitions (uses existing Copilot Coding Agent)

______________________________________________________________________

## Automated Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  AUTOMATED COPILOT ORCHESTRATION LOOP                           │
└─────────────────────────────────────────────────────────────────┘

1. Issue -> Copilot Assignment
   ├─ Trigger: Issue has label `status:queued` (or similar)
   ├─ Action: Tool assigns issue to @copilot via GitHub API
   └─ State: issue -> `in_progress`

2. Copilot Opens PR (Draft)
   ├─ Webhook: pull_request.opened (draft=true)
   ├─ Tool detects: PR linked to issue
   └─ State: PR -> `draft` | issue -> `pr_opened`

3. Copilot Marks PR Ready for Review
   ├─ Webhook: pull_request.ready_for_review
   ├─ Action: (none; Copilot auto-review is pre-configured in repo)
   └─ State: PR -> `ready_for_review`

4. Copilot Completes Code Review
   ├─ Webhook: pull_request_review.submitted + issue_comment (notification)
   ├─ Tool detects: "Copilot finished work" in comment
   ├─ Action: Tool posts comment: "@copilot apply changes based on the
   │          comments in [thread_link]" (customizable prompt template)
   └─ State: PR -> `changes_requested`

5. Copilot Implements Fixes (iterative)
   ├─ Webhook: pull_request.synchronize (new commits pushed)
   ├─ Check: CI status (check_suite.completed)
   ├─ If CI pass + no new review comments -> ready to merge
   └─ State: PR -> `merge_ready` (or loop back to step 4)

6. PR Merged
   ├─ Webhook: pull_request.closed (merged=true)
   ├─ Tool reads: "next issue" link from current issue description
   ├─ Action: Assign next issue to @copilot
   └─ State: issue -> `done` | next issue -> `in_progress` (goto step 1)

Edge Cases:
├─ CI failure -> Tool posts: "Fix CI failures; include RCA"
├─ Human review comments -> Tool waits for human approval before merge
└─ Ambiguous state -> Move to `needs_human` + notify
```

______________________________________________________________________

## Proposed State Machine (Labels)

### Issue States

- `status:queued` - Ready to work on
- `status:in_progress` - Copilot is working
- `status:pr_opened` - PR created, waiting for completion
- `status:done` - Issue completed and merged
- `status:needs_human` - Requires manual intervention

### PR States

- `status:draft` - Work in progress
- `status:ready_for_review` - Waiting for review
- `status:changes_requested` - Review feedback pending
- `status:ci_failed` - CI checks failing
- `status:merge_ready` - All checks passed, ready to merge
- `status:needs_human` - Requires manual intervention

______________________________________________________________________

## Phase 1 Dashboard (Minimal)

For Phase 1, dashboard shows:

**Home Page:**

- Recent webhook events (last 10) across all repos
- Quick stats: active issues/PRs, queue depth, error count
- Repo selector

**Repository Detail Page:**

- All webhook events (paginated/infinite scroll)
- Current active issue (if any) + state
- Current active PR (if any) + state + CI status
- Queue position (issues with `status:queued`)
- Health indicator (last event time, error count)

______________________________________________________________________

## Key Webhooks to Subscribe

Based on GitHub official documentation:

- `issues` (opened, labeled, assigned, closed)
- `issue_comment` (created)
- `pull_request` (opened, ready_for_review, synchronize, closed)
- `pull_request_review` (submitted)
- `pull_request_review_comment` (created)
- `check_suite` (completed)
- `check_run` (completed)

______________________________________________________________________

## Risk Register

| Risk                                                                         | Likelihood | Impact   | Mitigation                                                                                |
| ---------------------------------------------------------------------------- | ---------- | -------- | ----------------------------------------------------------------------------------------- |
| **Webhook delivery failures** (GitHub downtime, network issues)              | Medium     | High     | Retry logic + dead-letter queue; manual replay UI; health monitoring                      |
| **Copilot API/behavior changes** (notification format, assignment mechanics) | High       | High     | Graceful degradation; version detection; fail to `needs_human`; monitor GitHub changelogs |
| **CI flakiness** causing false positives                                     | High       | Medium   | Confidence thresholds; require N consecutive failures before action; human override       |
| **State machine race conditions** (concurrent webhooks for same PR)          | Medium     | High     | Idempotency keys; event ordering with timestamps; pessimistic locking                     |
| **Label conflicts** (human vs. tool editing labels)                          | Low        | Low      | Tool owns `status:*` namespace; document convention; detect conflicts → `needs_human`     |
| **Webhook signature spoofing**                                               | Low        | Critical | Mandatory signature verification; rotate secrets regularly; audit failed verifications    |
| **Event retention bloat** (1 year @ 43K events/day = 15M events)             | Medium     | Medium   | Partition by month; archive old events; efficient indexing; configurable retention        |
| **Serverless cold start latency**                                            | Medium     | Low      | Keep-alive pings; async processing queue; webhook retry tolerance                         |

______________________________________________________________________

## Non-Functional Requirements (NFRs)

### Security

- GitHub App with least-privilege scopes (read issues/PRs, write
  labels/comments/assignments)
- Webhook signature validation (HMAC-SHA256)
- Role-based access control (RBAC): Owner, Admin, Viewer
- Secrets stored in managed vault (not environment variables)
- Audit log for all automated actions (immutable, timestamped)

### Reliability

- **Webhook handler:**
  - Idempotent processing (delivery ID deduplication)
  - Retry with exponential backoff (GitHub redelivery support)
  - Dead-letter queue for persistent failures
- **Event processing:**
  - Asynchronous queue (webhook ingestion decoupled from processing)
  - Graceful degradation (partial failures don't block other repos)
- **Uptime:** 99% availability for webhook receiver

### Performance

- **Webhook ingestion:** \<500ms response time (200 OK fast return)
- **Event processing latency:** \<5 seconds from webhook → action execution
- **Dashboard load:** \<3 seconds for repo detail view (paginated events)
- **Event storage:** Support 50K events/month per repo with efficient querying

### Scalability

- Support 10 repos in MVP (design for 50+)
- Handle 50 events/minute burst (10 repos @ 5 events/min each)
- Horizontal scaling via queue workers (stateless processing)

### Observability

- Health endpoint (`/health`) for uptime monitoring
- Metrics: webhook delivery success rate, processing latency, queue depth
- Error logging with context (repo, issue, event type, stack trace)

### Maintainability

- State machine defined declaratively (YAML/JSON config)
- End-to-end test harness with replayable webhook fixtures
- CLI commands: `start`, `stop`, `restart`, `status`, `replay-event`

______________________________________________________________________

## Definition of Ready (DoR) Checklist

Before handoff to `@story-builder`, verified:

- [x] **User value is clearly stated** (reduce manual workflow steps by ≥80%)
- [x] **Success metrics are quantified** (time savings, action reduction,
  uptime)
- [x] **Acceptance criteria defined** (Phase 1: event stream + dashboard +
  webhook ingestion)
- [x] **Dependencies identified** (GitHub App created; webhook docs reviewed;
  tech stack confirmed)
- [x] **Out of scope explicitly listed** (no code diffs, no workflow editing,
  single-org only)
- [x] **Data model impact assessed** (need: Repository, EventReceipt, Issue,
  PullRequest, AuditLog entities)
- [x] **Security/privacy reviewed** (GitHub App auth, webhook signatures, RBAC,
  audit logs)
- [x] **UX states defined** (dashboard: repo list, event stream, current
  issue/PR, queue)
- [x] **Risk register created** (8 risks identified with mitigations)
- [x] **NFRs defined** (security, reliability, performance, scalability)
- [x] **Constraints documented** (FastAPI, SQLModel, PostgreSQL, SvelteKit,
  Tailwind CSS, uv, Docker, single-org, ≤10 repos)

______________________________________________________________________

## Next Steps

**Handoff to @story-builder** for INVEST-compliant user stories:

### Phase 1 User Stories

- GitHub App webhook receiver with signature verification
- Event stream storage (PostgreSQL/SQLite)
- Repository selection UI
- Event stream viewer (home page: recent 10; detail page: all paginated)
- Minimal dashboard (current issue, current PR, queue, health)
- CLI commands (start, stop, restart, status)

### Phase 2-3 User Stories

- State machine engine (issue/PR lifecycle)
- Automated actions (assign, label, comment)
- Queue management (single concurrency per repo)
- Policy configuration (repo-level overrides)

______________________________________________________________________

**Document generated by:** @requirements agent **Related documents:**

- [Original Requirements](copilot-workflow-orchestrator-requirements.md)
- [Web Dev Lifecycle Guide](best_practices/web-dev-lifecycle/)
