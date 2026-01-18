# Requirements Document — Copilot Workflow Orchestrator — Updated (Multi-Authorization / Multi-Installation)

## 1. Executive Summary

This product is a web service that orchestrates a **single-issue-at-a-time (per
repository/lane)** GitHub Copilot Code Agent workflow via **event-driven
automation**. It reduces human “message bus” work by listening to GitHub events,
applying pre-defined policies/actions, and (later phases) using AI to interpret
Copilot/CI signals for decision support. **Across multiple repositories, the
orchestrator can run multiple issues in parallel — one active issue per
repo/lane by default.**

**Key constraint:** AI is workflow-only (comments/notifications + prompt/config
review). It must not ingest or propose **source code diffs/implementation
changes**. In Phase 5 it may analyze **prompts and GitHub configuration** (from
Phase 2) and provide recommendations only.

**Key update (Event Stream):** The system must persist and display a **complete
time-ordered event stream** for selected repositories (not just the latest
event).

**Key update (Multi-Authorization):** The system must support **multiple GitHub
App installations/authorizations simultaneously** (across multiple GitHub
accounts and/or organizations, subject to user/admin granting permission). The
tool must record multiple installation contexts and operate across **multiple
selected repositories from different installations at the same time**, while
maintaining strict data isolation and correct token context per installation.

______________________________________________________________________

## 2. Goals and Success Metrics

### 2.1 Goals

- Minimize manual steps across: issue assignment → PR lifecycle → review cycles
  → CI failure remediation → merge readiness.
- Improve correctness and consistency by enforcing:
  - structured “prompt inputs” (templates/instructions) **read from repo**
  - hard GitHub gates (branch protections/rulesets) **read from GitHub**
- Provide operational visibility: **event timeline**, queue status, current work
  item, blockers, and audit trail.
- Introduce AI progressively: assist-first (explain scenario + recommend
  actions), later limited autonomous actions for low-risk cases only.
- **Enable multi-installation operations:** allow one tool instance to manage
  multiple installations concurrently, without cross-tenant data leakage.

### 2.2 Success Metrics (examples)

- ≥50–80% reduction in manual comments/label changes per PR lifecycle (baseline
  vs after).
- ≥30% fewer review/CI iterations per issue (first-pass quality proxy).
- Mean time from issue “ready” to merge-ready reduced without increasing defect
  rate.
- 100% auditable actions (no “silent automation”).
- **Zero cross-installation data leaks** (hard requirement) and clear
  attribution of every event/action to an installation context.

______________________________________________________________________

## 3. Non-Goals (Explicit Out of Scope)

- Modifying or generating code changes, reviewing code diffs, or making
  architecture decisions on diffs.
- Replacing GitHub Copilot; the tool orchestrates workflow around Copilot.
- Editing GitHub Actions workflow YAML (treated as code). Tool may show run
  results but should not edit workflows in MVP.
- Fully autonomous merging by default.
- Acting as a generic GitHub management console beyond the scope of Copilot
  workflow orchestration.

______________________________________________________________________

## 4. Users, Personas, and Use Cases

### 4.1 Personas

- **Maintainer/Owner:** Defines policies, monitors queue, approves high-risk
  steps.
- **Reviewer:** Consumes summaries, provides targeted approvals.
- **Operator (optional):** Manages multiple repos, watches for failures and
  bottlenecks.
- **Multi-Installation Admin (new):** Connects multiple GitHub installations
  (orgs/users), manages tool-side access control, and ensures repositories are
  correctly scoped per installation.

### 4.2 Primary Use Cases

- Select repositories to connect; view a **time-sequenced event stream** per
  repo.
- **Connect multiple GitHub installations** and select repositories under each
  installation; operate them concurrently.
- Batch-create issues, then let the tool queue and assign to Copilot one at a
  time.
- Automatically progress PR states based on checks and Copilot notifications.
- Automatically request Copilot to fix CI failures using a standard comment
  template.
- Provide a dashboard view of “what is happening now” across repos, with
  drill-down to event timelines.
- Use AI to explain “what happened / what to do next” and validate whether
  Copilot’s response is aligned with expectations.

______________________________________________________________________

## 5. Product Scope and Phasing (Updated Phases)

### Phase 1 — GitHub App + Webhook ingestion + Repo selection + Event Stream UI

**Objective:** Establish reliable integration and observability.

**Scope**

- GitHub App integration and installation onboarding.
- **Multi-installation onboarding (added):**
  - Support onboarding **multiple installations** (personal accounts and/or
    organizations).
  - Persist installation identities (installation ID, account/org identity,
    permissions snapshot, granted repository scope).
  - Tool-side access control mapping: which tool users can view/manage which
    installations and repositories.
- Webhook receiver with signature verification, retries, and idempotency.
- Repository selection UI (connect/disconnect repos).
- **Event Stream View (per selected repo)**:
  - Display **all received GitHub events** in **reverse chronological order**
    (newest first) with pagination/infinite scroll.
  - Show for each event:
    - received timestamp (+ GitHub event timestamp if available)
    - event type + action
    - actor (user/bot)
    - target object identifiers (issue/PR/check/workflow) + GitHub links
    - webhook delivery/event ID for dedup tracing
    - verification status (signature pass/fail)
    - processing status (received/processed/failed/retried)
    - **installation context (added): installation/account/org identity**
  - Filters: event type, action, actor, object number, time range, processing
    status, **installation/account**.
  - Read-only raw payload viewer (for debugging).
- Health summary (secondary): last event time, ingestion lag, retry/error
  counters, **per-installation health**.

**Acceptance Criteria**

- GitHub App can onboard repositories and start receiving webhooks reliably.
- UI displays a complete event timeline per repo; retries do not duplicate
  events.
- **Multiple installations can be connected concurrently; events/actions are
  correctly attributed to the right installation and never mixed.**

______________________________________________________________________

### Phase 2 — Show prompts and GitHub configurations (Read-only)

**Scope**

- Read-only **Prompt Catalog** (repo files):
  - issue templates, PR templates/checklists, agent instructions (AGENTS.md,
    CONTRIBUTING.md).
  - Persist snapshots/hashes and show diffs over time.
- Read-only **Policy Snapshot** (GitHub governance):
  - branch protection / rulesets (required checks, review requirements, merge
    restrictions).
  - Persist normalized snapshots and show change history.
- UI per repo: Prompts tab + Governance tab.
- **Multi-installation note:** prompts/config snapshots are stored **per
  installation + repo** and access-controlled accordingly.

______________________________________________________________________

### Phase 3 — State machine engine + allowlisted actions (automation backend)

**Scope**

- Deterministic state machine mapping GitHub events → workflow states, with
  idempotency.
- Per-repository single concurrency enforcement per repo/lane (**1 active issue
  per repo/lane**, while **multiple repos may run in parallel**).
- Allowlisted actions: labels, standardized comments, assign/unassign (including
  to Copilot), request review / draft-ready toggles (where supported).
- Immutable audit trail for all actions.
- Minimal admin controls: enable/disable automation; pause lane; force
  `needs_human`.
- **Multi-installation note:** all actions must execute under the correct
  installation token context.

______________________________________________________________________

### Phase 4 — Comprehensive UI dashboard (Ops-grade)

**Scope**

- Cross-repo dashboard: current active issue/PR, queue, blockers, CI/check
  summaries.
- Drill-down timeline replay combining: GitHub events + tool actions.
- Audit explorer: search/filter.
- Template library management + tool policy editor (still not writing GitHub
  governance by default).
- **Multi-installation note:** dashboard supports grouping/filtering by
  installation/account/org.

______________________________________________________________________

### Phase 5 — AI Assist-only (workflow + prompt/config optimization; no execution)

**Scope**

- AI generates situation reports on key events (CI fail, Copilot done, review
  comments posted).

- AI classifications + confidence:

  - CI failure category (lint/type/test/flaky/infra/unknown)
  - whether Copilot response addresses review comments
    (yes/no/partial/uncertain)
  - whether completion aligns with acceptance criteria
    (yes/no/partial/uncertain)

- **Self-improvement loop (added):** AI analyzes the **prompts and GitHub
  configuration** surfaced in **Phase 2** and produces recommendations to make
  the system work better (higher code quality, stricter lint adherence, better
  requirement fulfillment).

  - Prompt quality review: clarity, completeness, “definition of done”,
    test/lint expectations, safe autonomy boundaries, and consistency across
    repos.
  - GitHub governance review: rulesets/branch protection/required
    checks/CODEOWNERS/merge settings; identify gaps that reduce CI gating or
    allow low-quality merges.
  - CI/workflow alignment review (config-level): ensure “required checks” match
    real workflow names, lint/type/test gates exist, and permissions/concurrency
    are sane.
  - Output format: prioritized recommendations with rationale, expected impact,
    risk level, and suggested text/config edits **as proposals**.

- AI outputs are advisory only; stored and auditable.

- **No write-back in Phase 5:** the system must not auto-modify prompts or repo
  configuration. Any controlled write-back is deferred to Phase 7+.

- **Multi-installation note:** AI assessments are scoped to installation + repo
  and must not cross-leak data.

______________________________________________________________________

### Phase 6 — Selective autonomy (guarded low-risk auto-actions)

**Scope**

- AI+rules may execute only allowlisted low-risk actions with confidence
  thresholds and optional human approval.
- Dry-run mode.
- Global/per-repo kill switch.
- Fail-closed on ambiguity.
- **Multi-installation note:** kill switches and policies support
  installation-level and repo-level scoping.

______________________________________________________________________

### Phase 7 — Controlled write-back (change-managed prompts & GitHub governance)

**Scope**

- Modify prompts/configs from UI in a change-managed way:
  - prompts: open PRs for repo-file changes preferred
  - GitHub governance: proposed changes require owner approval + rollback plan
- Full change records and diffs.
- **Multi-installation note:** change requests must be executed only within the
  installation that owns the target repo.

______________________________________________________________________

### Phase 8 — Analytics & scale operations (optional)

**Scope**

- Cycle-time analytics, bottleneck detection, CI failure trend reporting.
- Org-level policy packs and multi-tenant separation (if needed).
- Event replay/testing harness; SLO/alerting integration (optional).
- **Multi-installation note:** analytics must support strict tenant isolation
  and optionally aggregated reporting where explicitly permitted.

______________________________________________________________________

## 6. Functional Requirements

### 6.1 GitHub Integration

**FR-1:** The system shall authenticate as a **GitHub App** (not PAT) with
least-privilege permissions. **FR-2:** The system shall subscribe to and process
GitHub webhooks for relevant events, including at minimum:

- Issues: opened/labeled/assigned/unassigned/closed/reopened
- Issue comments
- Pull requests: opened/synchronized/ready_for_review/closed/merged
- PR reviews + review comments
- Check runs / check suites / workflow runs (CI status)

**FR-3:** The system shall support programmatic issue assignment to Copilot
and/or Copilot trigger mechanisms (validate supported endpoints during
implementation).

**FR-3a (added, Multi-Authorization):** The system shall support **multiple
concurrent GitHub App installations** and persist installation metadata
(installation ID, account/org identity, permissions snapshot, granted repository
scope).

**FR-3b (added, Token Context):** The system shall mint and use API credentials
**scoped to the correct installation context** for every API call and action
execution. The system shall never assume one authorization spans multiple
installations.

**FR-3c (added, Tool-side Access Control):** The system shall enforce tool-side
access control so a tool user can only view/manage the installations and
repositories they have been granted.

### 6.2 Event Stream (New / Updated)

**FR-4:** The system shall persist **all received webhook events** (metadata +
payload reference) per selected repository. **FR-5:** The system shall render a
**time-ordered event stream** (default newest-first) with pagination and
filtering. **FR-6:** Each event record shall include: timestamps (received +
source), event type/action, actor, target object IDs/links, delivery/event ID,
verification status, processing status, and raw payload (read-only viewer).
**FR-6a (added):** Each event record shall include **installation context**
(installation ID and account/org identity) and the UI shall allow
filtering/grouping by installation.

### 6.3 Prompt & Configuration Read (Initial Read-only)

**FR-7:** The system shall read and render repository “prompt artifacts”
(read-only in Phase 2), including:

- Issue templates
- PR templates/checklists
- Repository agent instructions (e.g., AGENTS.md, CONTRIBUTING.md)

**FR-8:** The system shall read and render GitHub repository governance
configuration (read-only in Phase 2), including:

- Branch protection / rulesets (required checks, review requirements, merge
  restrictions)

**FR-9:** The system shall persist a version/hash snapshot of prompt/config
artifacts for traceability. **FR-9a (added):** Snapshots shall be stored **per
installation + repository** and access-controlled.

### 6.4 Queue Management (Single Concurrency Discipline)

**FR-10:** The system shall maintain a queue per repository (or per configured
“lane”) and enforce **max concurrency = 1** by default. **FR-10a
(clarification):** Concurrency is enforced **per repository/lane**; the system
may have one active issue in each selected repository at the same time.
**FR-11:** The system shall support issue intake into queue based on triggers:

- Label-based (e.g., `agent:queued`)
- Manual “enqueue” action from UI **FR-12:** When capacity is available, the
  system shall select the next queued issue and initiate Copilot
  assignment/trigger.

### 6.5 State Machine (Workflow Orchestration)

**FR-13:** The system shall implement an explicit state machine for Issue/PR
lifecycle (example baseline states):

- queued
- in_progress (Copilot working)
- pr_opened_draft
- needs_review (ready for review)
- changes_requested (review feedback pending)
- ci_failed
- merge_ready
- done/merged
- needs_human (fail-closed fallback)

**FR-14:** The system shall map GitHub events → state transitions
deterministically, with idempotency (webhook retries). **FR-15:** The system
shall support per-repo policy overrides for allowed transitions and actions.
**FR-15a (added):** The system shall support installation/org-level defaults
with per-repo overrides, without violating repo-specific governance constraints.

### 6.6 Pre-defined Actions (Allowlist)

**FR-16:** The system shall support an allowlisted set of actions, configurable
per repo:

- Add/remove labels
- Post standardized comments (templates)
- Assign/unassign issue (including to Copilot)
- Request review / set PR to draft/ready (where supported)
- Trigger rerun of workflows (optional; gated)

**FR-16a (added):** All actions shall be executed under the correct
**installation token context** and recorded accordingly in audit logs.

**FR-17:** The system shall store comment templates, including:

- “Please fix CI failures first; include RCA and what changed”
- “Please address review comments; summarize changes”
- “Provide completion summary mapped to acceptance criteria”

### 6.7 UI & Status Reporting (Updated)

**FR-18:** The system shall provide a dashboard that shows, at minimum:

- Selected repositories and connectivity/health
- **Event stream access** (time-sequenced events)
- Current active issue/PR per repo
- Queue list and position
- Latest Copilot notification/status
- CI status summary and failing checks
- Blockers and next recommended action
- **Connected installations/accounts and per-installation health (added)**

**FR-19:** The system shall provide detailed views:

- **Full event timeline** (filters + raw payload viewer)
- Issue timeline summary (events, labels, assignments)
- PR health: checks, review status, latest automation actions
- Prompt Catalog (read-only in Phase 2)
- Policy Snapshot (read-only in Phase 2)
- **Installation scope view (added): list installations → repos →
  event/action/audit drill-down**

### 6.8 Audit, Traceability, and Controls

**FR-20:** The system shall record an immutable audit trail for every
automated/manual action:

- timestamp, actor (system/user/AI-advice), inputs, rationale, outcome, related
  GitHub URLs/IDs **FR-21:** The system shall support “dry-run mode”
  (recommended Phase 6; optional earlier) to simulate actions without executing
  them. **FR-22:** The system shall fail closed: when uncertain/conflicting
  signals, move workflow to `needs_human`.

**FR-20a (added):** Every audit record shall include **installation context**
(installation ID + account/org identity) and the credential context used for
execution.

______________________________________________________________________

## 7. AI Requirements (Workflow-only)

### 7.1 Data Boundaries (Hard Constraint)

**AI-1:** AI shall ingest only workflow artifacts, including:

- issue/PR text, comments, Copilot notifications, check results summaries
- **Phase 2 snapshots:** repository prompts/templates (e.g., AGENTS.md /
  instructions) and GitHub configuration metadata (rulesets, branch protection,
  required checks, merge policies; and workflow/CI configuration summaries)

**AI-2:** AI shall not ingest or analyze **source code diffs/patches** and shall
not propose **implementation changes to application code**.

- **Allowed in Phase 5:** AI may propose **text/config improvements** to prompts
  and GitHub configuration as recommendations only (no automatic changes).

**AI-2a (added):** AI processing must be scoped to **installation + repo**.
There must be no cross-installation data exposure in prompts, context windows,
embeddings, or logs.

### 7.2 Assist-first Capabilities (Phase 5)

**AI-3:** AI shall generate a “situation report” on key events (CI fail, Copilot
done, review comments posted):

- what happened, why it matters, recommended next action, confidence score

**AI-4:** AI shall classify scenarios:

- CI failure category (lint/type/test/flaky/infra/unknown)
- “Copilot response likely addresses review comments” (yes/no/partial/uncertain)
- “Completion aligns with acceptance criteria” (yes/no/partial/uncertain)

**AI-5 (added):** AI shall analyze **Phase 2 prompts and GitHub configuration**
and produce recommendations to improve Copilot workflow outcomes (quality, lint
adherence, requirements fulfillment):

- prompt quality gaps, inconsistencies, and missing “definition of done”
- governance gaps (rulesets/branch protections/required checks/CODEOWNERS/merge
  policies)
- CI/workflow alignment issues (required checks naming mismatch, missing
  lint/type/test gates, overly-broad permissions)
- output must be **advisory**, **auditable**, and scoped to installation + repo

### 7.3 Future Autonomy (Phase 6+ Guarded)

**AI-5:** AI-recommended actions may be executed automatically only if:

- scenario matches allowlisted low-risk policy
- confidence above threshold
- and/or human approval captured (configurable)

______________________________________________________________________

## 8. Non-Functional Requirements

### 8.1 Security & Permissions

- Least-privilege GitHub App permissions; per-org install scoping.
- Secrets stored in managed vault; rotate keys; webhook signature verification.
- Role-based access control (RBAC) in the UI (Owner/Admin/Viewer).
- Full audit logging; no “hidden” automation.
- **Tenant isolation (added):** strict separation across installations; no
  cross-installation read access unless explicitly granted inside the tool.

### 8.2 Reliability & Scale

- Webhook handler must be idempotent and retry-safe.
- Event ingestion decoupled from processing (queue/message bus recommended).
- Rate limiting/backoff for GitHub API calls.
- Multi-tenant readiness (org/repo isolation) if applicable.
- **Per-installation rate/health management (added):** track API usage and error
  budgets per installation to prevent one installation from degrading all
  others.

### 8.3 Performance

- Event stream and dashboard updates: near real-time (seconds-level).
- Support high event volume with pagination and indexed filters.
- Ability to support N repos and M concurrent webhooks with predictable
  throughput (**1 active issue per repo/lane**, with **parallelism across
  repositories**).
- **Multi-installation scaling (added):** indexing and partitioning strategy
  must support filtering by installation efficiently.

### 8.4 Maintainability

- Policy engine and state machine are declarative and testable.
- End-to-end test harness with replayable webhook fixtures.
- **Multi-installation test coverage (added):** automated tests must include
  cross-installation isolation assertions.

______________________________________________________________________

## 9. Data Model (High-Level)

Entities (minimum):

- Repository
- Installation
- **InstallationAccess** (added): mapping of tool users/roles to installations
  and/or repositories
- **EventReceipt** (event type/action, timestamps, delivery ID, actor, target
  object IDs, verification status, processing status, payload reference,
  **installation context**)
- Issue (queue metadata, state, labels, Copilot assignment marker)
- Pull Request (state, linked issue, checks summary, review summary)
- Workflow Run / Check (status, conclusion, timestamps, summary pointers)
- Prompt Artifact Snapshot (file path, hash, content pointer, **installation
  context**)
- Policy Snapshot (normalized JSON, hash, **installation context**)
- Audit Log Entry (**includes installation context and credential context**)
- AI Assessment (scenario, classification, confidence, explanation,
  **installation context**)

______________________________________________________________________

## 10. Configuration Model (Now vs Future)

### Phase 1–2 (Read-only)

- Read prompt artifacts from repo files.
- Read GitHub governance configuration from APIs.
- Store snapshots and render in UI.
- **Multi-installation configuration (added):** store installation metadata and
  tool-side access control policies; all snapshots are keyed by installation +
  repo.

### Phase 6–7 (Controlled write)

- Allow editing non-code configs and comment templates in tool UI.
- Preferred: open PRs for prompt file changes rather than direct pushes.
- Any GitHub configuration writes must be gated (owner approval + audit +
  rollback plan).
- **Multi-installation constraint (added):** writes must execute only within the
  owning installation context and only by tool users authorized for that
  installation.

______________________________________________________________________

## 11. Risks and Open Questions (Explicit)

- GitHub API coverage varies by feature (rulesets/branch protections/assignment
  mechanics). Confirm endpoints early and design fallbacks.
- Copilot notification formats may change; implement robust parsing with
  graceful degradation.
- False positives in AI classification can create churn; keep fail-closed
  defaults and human approvals initially.
- Over-automation can mask real quality problems; metrics must track defect
  leakage, not just speed.
- High event volumes require careful retention and indexing; define retention
  windows early.
- **Multi-installation complexity (added):** permissions variance, partial
  access, and rate-limit variance across installations; ensure isolation and
  clear operator UX.
- **Org install approval (added):** some orgs require admin approval for app
  installation; onboarding must handle “pending approval” states.

______________________________________________________________________

## 12. Acceptance Criteria (Updated)

- A GitHub App installation can onboard repositories and start receiving
  webhooks reliably.
- The tool can display:
  - **full time-sequenced event stream** per repo (not only latest)
  - queue + current active item
  - PR status + CI summary
  - Prompt Catalog snapshots (read-only in Phase 2)
  - Policy Snapshot (read-only in Phase 2)
- The tool can enforce **per-repository** single concurrency and auto-assign
  next queued issue to Copilot (Phase 3) — i.e., **1 active issue per
  repo/lane**, with multiple repos in parallel.
- On CI failure, the tool posts the standardized “Fix CI + RCA” comment and
  transitions state (Phase 3).
- Every action is logged with traceability.
- AI produces situation reports and prompt/config optimization recommendations
  without executing actions (Phase 5).
- **Multi-authorization acceptance (added):**
  - The tool can connect to multiple installations concurrently.
  - All events/actions/audits are correctly attributed to installation context.
  - No user can view/manage repos outside their tool-granted installation scope.

______________________________________________________________________
