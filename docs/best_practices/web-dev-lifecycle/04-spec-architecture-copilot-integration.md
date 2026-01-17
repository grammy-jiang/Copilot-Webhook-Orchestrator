# Spec/Architecture Stage: Copilot Generates Diagrams + Contracts; You Own Tradeoffs + Risk (Practical + Repeatable)

If you want Copilot to *improve* specs (not just produce pretty docs), you need
a **contract-first workflow** with **hard gates**: ADRs, NFRs, threat model, and
“spec PR before code PR.” Copilot’s role is **drafting + consistency checking +
scaffolding**. Your role is **architectural choices and risk ownership**.

______________________________________________________________________

## A. Baseline setup (so Copilot doesn’t invent architecture)

### 1) Repo instructions = “architecture policy”

- Use repository-wide custom instructions in `.github/copilot-instructions.md`
  and path-specific instructions via `.github/instructions/NAME.instructions.md`
  with `applyTo`. Avoid conflicting rules because conflict resolution can be
  non-deterministic.
- Use `AGENTS.md` to define agent governance and boundaries (what each agent
  may/may not do).

**Non-negotiables to encode**

- **Contract-first**: API/data contracts must be defined (OpenAPI/Schema) before
  implementation.
- **Decision logging**: any non-trivial tradeoff must produce an ADR.
- **NFRs mandatory**: security, privacy, performance, reliability,
  observability.
- **No silent scope creep**: explicitly list assumptions, open questions, and
  out-of-scope.
- **No new dependencies by default**: require explicit approval.

### 2) Prompt files = “SOP commands”

- Store repeatable prompts under `.github/prompts/*.prompt.md` and run them
  on-demand in chat.
- Keep them small and versioned so you can adapt if upstream behavior changes.

### 3) Custom agents = “specialized roles”

- Define custom agents as `.agent.md` profiles under `.github/agents/` (Markdown
  \+ YAML frontmatter; tools/models/behavior).

______________________________________________________________________

## B. Spec-to-code workflow with Copilot embedded (end-to-end)

### 1) Architecture intake → “Architecture brief”

**Goal:** turn a feature brief into an engineering-ready scope and constraints.

**Inputs you provide**

- user goal + success metric
- known constraints (compliance, data residency, latency, scale, cost)
- integration points (existing services, DBs, third-party APIs)

**Copilot outputs (drafts)**

- an **architecture brief**: context, goals/non-goals, constraints, quality
  attributes, risks, open questions
- candidate solution options (2–3) with pros/cons

**Gate:** if constraints and NFRs aren’t explicit, you’re not ready to design.

______________________________________________________________________

### 2) Diagram generation → “make flows legible”

**Goal:** reduce misinterpretation.

**Copilot does**

- generates Mermaid/PlantUML diagrams from the brief:
  - system context + container diagram (C4 style)
  - sequence diagram for critical flows
  - deployment diagram (high-level)

**Gate:** diagrams must match the contract + chosen option; no “diagram-only
architecture.”

______________________________________________________________________

### 3) Contract drafting → “OpenAPI + schemas + error model”

**Goal:** enable parallel frontend/backend development and prevent interface
drift.

**Copilot does**

- drafts OpenAPI endpoints (request/response schemas, pagination, filtering)
- defines a consistent **error model** (error codes, HTTP mapping, problem+json
  pattern if desired)
- proposes auth patterns (scopes/roles) and versioning strategy

**Gate:** every endpoint must have:

- auth requirement
- success + failure responses
- validation constraints
- idempotency guidance where relevant

______________________________________________________________________

### 3.5) Contract tests → "TDD for APIs" (NEW)

**Goal:** write contract tests alongside contracts—tests exist before
implementation.

Following TDD principles, **contract tests are written when contracts are
defined**, not after implementation. This ensures the contract is implementable
and verifiable.

**Copilot does**

- drafts contract test stubs from OpenAPI specs
- generates test cases for:
  - each endpoint's success responses
  - each error response (validation, auth, not found)
  - pagination and filtering behavior
  - schema validation (required fields, types, constraints)

**TDD integration:**

- Contract tests are the **Red phase** for API development
- Tests fail until the API is implemented correctly (Green phase)
- Tests are deterministic, isolated, and run in CI

## **Gate:** no implementation starts until contract tests exist for critical endpoints.

### 4) Data model & migrations → “DB contracts”

**Goal:** make persistence changes explicit and reversible.

**Copilot does**

- drafts entity relationships, indexes, and migration outline
- proposes backward/forward compatibility steps (expand → backfill → switch →
  contract)

**Gate:** migration + rollback plan required before coding.

______________________________________________________________________

### 5) Risk control → “Threat model + abuse cases + NFR checklist”

**Goal:** prevent avoidable security and operational incidents.

**Copilot does**

- threat model draft (assets, entry points, trust boundaries)
- abuse cases (rate-limit bypass, privilege escalation, data leakage)
- NFR checklist with target numbers (SLOs, latency budgets, retention, audit)

**Gate:** any high-risk item must have mitigation + ownership.

______________________________________________________________________

### 6) Decision capture → “ADRs”

**Goal:** record why you chose option A over B.

**Copilot does**

- drafts ADRs: context, decision, alternatives, consequences
- links ADRs to diagrams/contracts

**Gate:** “no ADR, no merge” for major decisions.

______________________________________________________________________

### 7) Handoff to implementation → “spec PR → code PR”

**Goal:** force alignment and reduce churn.

**Copilot does**

- creates a task breakdown (backend, frontend, tests, observability, rollout)
- generates a feature-level “definition of done”

**Gate:** spec PR approved before implementation PR starts (except small
patches).

______________________________________________________________________

## C. Where Copilot CLI / Coding Agent fits (high-ROI here)

- Use Copilot CLI to delegate spec artifact generation to the coding agent and
  get a PR back (e.g., add diagrams, OpenAPI file, ADR templates).
- Governance model: agent writes docs/contracts in a branch → opens PR → you
  review/merge.
- Treat agent outputs like any other contributor: PR template, CI checks, and
  reviewer gate remain mandatory.

______________________________________________________________________

## D. Recommended custom agents for the spec stage (keep it pragmatic)

### 1) `arch-spec-author.agent.md` (primary agent)

**Mission:** produce a coherent spec package (brief + diagrams + contracts + ADR
drafts).

**Non-negotiables**

- contract-first (OpenAPI/schema before code)
- include NFRs + risk register + open questions
- no dependency changes unless requested
- produce spec artifacts in predictable paths

### 2) `risk-and-nfr-gate.agent.md` (quality gate agent)

**Mission:** act as a skeptical reviewer focused on risk, security, and
operability.

**Non-negotiables**

- threat model + abuse cases required
- explicit mitigations and ownership
- observability requirements (logs/metrics/traces) must be defined
- rollout/rollback strategy must exist

### Optional skills (finer modularity)

- `openapi-architect` — OpenAPI + error model + versioning rules
- `diagram-smith` — Mermaid/C4/sequence generation from brief
- `adr-writer` — ADR creation + consistency linking
- `migration-planner` — safe migration sequencing + rollback plan

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store these in `.github/prompts/` and invoke via `/...` in chat:

- `/arch-brief-from-feature` → architecture brief + options + open questions
- `/generate-diagrams` → context/container/sequence/deploy diagrams
- `/draft-openapi-contract` → OpenAPI + schemas + error model
- `/data-model-and-migrations` → entities/indexes + migration/rollback plan
- `/threat-model-and-abuse-cases` → risk register + mitigations
- `/write-adrs` → ADR(s) for key decisions
- `/handoff-to-implementation` → tasks + DoD + rollout plan

______________________________________________________________________

## Example prompt file skeleton (contract + diagrams)

```markdown
---
name: draft-openapi-and-diagrams
description: Produce OpenAPI contract + core diagrams from an architecture brief
agent: arch-spec-author
tools: [workspace]
---

Input: ${input:arch_brief:Paste the architecture brief}

Rules:
- Contract-first: define OpenAPI endpoints + schemas + error model.
- Generate Mermaid diagrams: context, container, sequence for top 2 flows.
- Do not invent external systems; list unknowns as open questions.
- Include auth requirements, failure responses, validation constraints.
- Include NFRs and a risk register with mitigations.

Deliverables:
1) docs/architecture/ARCH_BRIEF.md
2) docs/diagrams/*.mmd
3) docs/api/openapi.yaml
4) docs/adr/ADR-*.md (drafts)
5) docs/risk/RISK_REGISTER.md
```

______________________________________________________________________

## Next step suggestion

The following artifacts are now available in this repository:

- `.github/agents/arch-spec-author.agent.md` ✅
- `.github/agents/risk-and-nfr-gate.agent.md` ✅
- `.github/copilot-instructions.md` ✅ With architecture output rules
- `.github/instructions/issue-output.instructions.md` ✅ With ADR format

### Issue Templates for Architecture Stage

| Template                       | Use When           | Key Fields                                           |
| ------------------------------ | ------------------ | ---------------------------------------------------- |
| `04-architecture-decision.yml` | Documenting ADRs   | Context, Options, Decision, Consequences, NFR Impact |
| `05-technical-debt.yml`        | Tracking tech debt | Risk Level, NFR Impact, Refactor Scope               |
