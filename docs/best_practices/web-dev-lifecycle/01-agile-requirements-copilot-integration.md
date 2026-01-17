# Agile Feature Requirements Gathering: How to Integrate GitHub Copilot (Practical + Repeatable)

If you want Copilot to *raise* requirement quality (not just generate text), you
need an **operating model** with **artifacts, gates, and reusable prompts**.
Treat Copilot outputs as **drafts + hypotheses**; you own scope, priority, and
risk.

______________________________________________________________________

## A. Baseline setup (so Copilot stays on-rails)

### 1) Repo-wide instructions = “policy”

- Use `.github/copilot-instructions.md` to encode your consistent rules: story
  format, required fields, definition of ready, security/privacy baselines, tech
  constraints.
- Add **path-specific instructions** under
  `.github/instructions/*.instructions.md` for product docs vs engineering docs
  (avoid conflicting rules; instruction resolution can be unpredictable when
  rules collide).

> **This repo provides:** `.github/copilot-instructions.md` with INVEST, DoR,
> and issue template integration rules.

### 2) Prompt files = "playbooks"

- Put reusable prompts in `.github/prompts/*.prompt.md`.
- Use YAML frontmatter (e.g., `name`, `description`, `agent`, `tools`) so each
  prompt behaves like a standard operating procedure you can invoke repeatedly.

> **This repo provides:** `.github/prompts/story-to-issue-form.prompt.md` for
> converting stories to issue form format.

### 3) Issue Forms = "structured intake"

- Use GitHub **Issue Forms** (`.github/ISSUE_TEMPLATE/*.yml`) to force required
  fields.
- Agent outputs should match issue form structure for easy copy-paste or direct
  creation.

> **This repo provides:**
>
> - `01-feature-request.yml` — Feature intake with problem/solution/metrics
> - `02-user-story.yml` — INVEST story with AC and DoR checklist

### 4) Grounding = "don't hallucinate the system"

- In VS Code chat, use workspace grounding (e.g., `@workspace`) so Copilot
  aligns with your actual repository conventions and existing patterns.

______________________________________________________________________

## B. Agile requirements workflow, with Copilot embedded (end-to-end)

### 1) Intake → “Feature one-pager”

**Goal:** convert raw ideas into a crisp, testable problem statement.

**You provide (inputs):**

- Problem + users + “why now”
- Success metric (what changes if we win)
- Constraints (time, compliance, platform, dependencies)

**Copilot does (drafts):**

- A **one-pager** with: Problem, Goals, Non-goals, Assumptions, Open questions,
  Risks, Metrics, Milestones
- A **clarifying questions list** (often the highest ROI output)

**Gate/guardrail:** if there’s no measurable success metric and no explicit
non-goals, the “requirement” is not ready.

**Reusable prompt idea (VS Code chat):**

> Convert these notes into a feature one-pager. Be skeptical: list assumptions,
> open questions, and risks. Output in a strict template.

______________________________________________________________________

### 2) Discovery → “Risks + edge cases + constraints”

**Goal:** expose landmines early (permissions, data, privacy, scalability,
migrations).

**Copilot does:**

- Generates a **risk register**: security, privacy, abuse cases, operational
  risks
- Drafts **NFRs** (non-functional requirements): latency, availability, audit,
  rate limits, observability hooks
- Lists **dependencies**: APIs, tables, services, third parties

**Your job:** decide tradeoffs; reject fantasy constraints.

______________________________________________________________________

### 3) Story mapping & slicing → “Epics → Stories (INVEST)”

**Goal:** break the feature into deliverable slices that can ship incrementally.

**Copilot does:**

- Proposes **user journey steps** and a story map
- Generates **small stories** aligned to slices (happy path first, then
  hardening)
- Proposes explicit **out-of-scope** items (scope control)

**Gate/guardrail:** any story that can’t be acceptance-tested is not a story;
it’s a vague wish.

______________________________________________________________________

### 4) Acceptance criteria (BDD) → “Given/When/Then + negative cases”

**Goal:** turn “we think” into **verifiable behavior**.

**Copilot does:**

- Writes Given/When/Then acceptance criteria
- Enumerates negative cases: auth failures, empty state, concurrency, timeouts,
  idempotency, partial failures

**Your job:** confirm business meaning; remove contradictions.

______________________________________________________________________

### 5) Definition of Ready (DoR) gate → “Backlog hygiene”

**Goal:** stop half-baked work entering implementation.

**Copilot can run a DoR checklist:**

- User value stated?
- Success metric defined (ideally quantified)?
- Acceptance criteria complete?
- Dependencies known?
- Data model touched (yes/no)?
- Migration/rollback considered?
- Security/privacy considered?
- Telemetry/observability defined?

If “no” on key items → story returns to refinement.

______________________________________________________________________

### 6) Sprint planning support → “Tasks + estimates (bounded)”

**Goal:** reduce planning overhead without letting AI invent schedules.

**Copilot does:**

- Breaks a story into engineering tasks (backend, frontend, migration, tests,
  telemetry)
- Highlights risky tasks and unknowns

**Gate/guardrail:** Copilot can suggest relative sizing, but estimation
commitments remain your call.

______________________________________________________________________

## C. Where Copilot Coding Agent / CLI fits (even in requirements stage)

This stage is mostly text + structure, but Copilot Coding Agent can still be
useful for **repo artifacts** (templates, docs, scaffolding):

- **Create/update requirement templates** (issue forms, docs structure) via PR.
- Use Copilot CLI to delegate structured work (e.g., generate templates,
  reorganize docs, add checklists) and get a draft PR back.
- Keep governance tight: require human review for merges, and treat agent
  outputs like any other contributor.

______________________________________________________________________

## D. Recommended “custom agents” for this step (keep it lean)

For Feature Requirements Gathering, don’t over-fragment. A pragmatic approach:

### One custom agent (“requirements”) + multiple prompt files

- **Agent**: `requirements` = consistent voice, skepticism, templates, DoR/AC
  standards.
- **Prompt files** (commands):
  - `/intake-onepager`
  - `/discover-risks-nfr`
  - `/slice-stories`
  - `/write-acceptance-criteria`
  - `/dor-check`

Prompt files live in `.github/prompts/*.prompt.md` and can set `agent:` plus
tools.

______________________________________________________________________

## Example prompt file skeleton

```markdown
---
name: intake-onepager
description: Turn raw notes into a feature one-pager with open questions and risks
agent: agent
---
You are the Requirements Analyst.
Input: ${input:notes:Paste raw notes}

Output a one-pager with:
- Problem / Users / Goals / Non-goals
- Success metrics (quantified)
- Assumptions
- Open questions (ranked by risk)
- Dependencies
- Risks + mitigations

Be skeptical and avoid inventing facts.
```

______________________________________________________________________

## Next step suggestion

If you want to proceed one-by-one, the next concrete deliverable is to produce:

- `requirements.agent.md` (the agent's stable "constitution") ✅ **Available in
  this repo**
- Prompt files in `.github/prompts/*.prompt.md` ✅
  **`story-to-issue-form.prompt.md` available**
- `.github/copilot-instructions.md` that enforces DoR, story format, and
  acceptance criteria rules ✅ **Available in this repo**
- Issue forms in `.github/ISSUE_TEMPLATE/` ✅ **8 templates available**

______________________________________________________________________

## Issue Template Reference

| Template                 | Use When           | Key Fields                                  |
| ------------------------ | ------------------ | ------------------------------------------- |
| `01-feature-request.yml` | New feature intake | Problem, Solution, Metrics, Constraints     |
| `02-user-story.yml`      | Backlog stories    | User Story, AC, DoR Checklist, Out of Scope |
