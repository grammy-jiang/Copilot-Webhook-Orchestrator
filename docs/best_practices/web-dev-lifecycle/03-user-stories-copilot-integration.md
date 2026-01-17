# User Stories: Integrating GitHub Copilot + Custom Agents (Practical + Repeatable)

If you want Copilot to *improve* story quality (not just generate text), treat
user stories as **structured backlog assets** with **hard gates**: INVEST, 3Cs,
acceptance criteria, and Definition of Ready. Copilot is best used as a
**drafting + consistency engine**, not as the decision-maker.

______________________________________________________________________

## A. Baseline setup (so Copilot doesn’t produce fluffy stories)

### 1) Repo instructions = “story policy”

- Put global rules in `.github/copilot-instructions.md` (story template, DoR
  expectations, language/format consistency).
- Add path-specific rules in `.github/instructions/*.instructions.md` with
  `applyTo` so story-related docs and templates get stricter constraints than
  normal code files.
- Use `AGENTS.md` to define agent governance (what each agent may/may not do).

**Non-negotiables to encode**

- Stories must meet **INVEST** and include **acceptance criteria**.
- Every story must include **edge/negative cases** (auth, empty, validation,
  error, concurrency if applicable).
- **No “big-bang” stories**: if it can’t ship in an iteration, it must be
  sliced.
- Explicit **out-of-scope** and **open questions** are mandatory.

### 2) Prompt files = “SOP commands”

- Store prompt files in `.github/prompts/*.prompt.md`.
- Enable prompt files in VS Code settings (`"chat.promptFiles": true`) and run
  them via `/PROMPTNAME`.
- Keep them small and versioned to tolerate upstream changes.

### 3) Issue Forms = “structured intake that prevents garbage”

- Use GitHub **Issue Forms** (`.github/ISSUE_TEMPLATE/*.yml`) to force required
  fields (persona, value, AC, DoR checkboxes).
- Prefer the `ISSUE_TEMPLATE/` directory approach; don’t build new process on
  deprecated legacy templates.
- Keep the form minimal: required fields + a DoR checklist + links to supporting
  docs.

> **This repo provides:** `.github/ISSUE_TEMPLATE/02-user-story.yml` with:
>
> - User story statement (As a / I want / So that)
> - Business value
> - Acceptance criteria: Happy path (Given/When/Then)
> - Acceptance criteria: Edge cases (empty, permission, validation, network)
> - Out of scope (required)
> - Dependencies
> - Open questions
> - DoR checklist (10 items)
> - Estimated complexity

______________________________________________________________________

## B. User-story workflow with Copilot embedded (end-to-end)

### 1) Story intake → “Story Candidate Set”

**Goal:** translate a requirement into multiple candidate stories (not one
bloated story).

**You provide:**

- feature brief (problem, users, constraints, success metric)
- any UX notes (links to designs if available)

**Copilot outputs:**

- a **candidate set**: 3–10 small stories mapped to a user journey
- explicit **assumptions + open questions**
- a recommended slicing strategy (MVP path first)

**Gate:** if Copilot can’t propose a sliceable journey, your brief is likely
under-specified.

______________________________________________________________________

### 2) INVEST enforcement → “Rewrite or reject”

**Goal:** eliminate vague and oversized stories.

**Copilot does:**

- checks each story against INVEST
- rewrites stories that fail (make it testable, reduce scope)
- flags “epic disguised as story” (common failure mode)

**Gate:** any story that fails “Testable” or “Small” goes back to refinement.

______________________________________________________________________

### 3) 3Cs completion → “Card → Conversation → Confirmation”

**Goal:** ensure the story isn’t just a one-liner.

**Copilot does:**

- **Card**: crisp statement and business value
- **Conversation**: clarification questions and decisions needed
- **Confirmation**: acceptance criteria (BDD) + examples

**Gate:** no AC = not ready.

______________________________________________________________________

### 4) Acceptance Criteria (BDD) → “Given/When/Then + negative cases”

**Goal:** make the behavior verifiable—and **test-first ready**.

Acceptance criteria are the **foundation for TDD**: they become test cases
before implementation begins. Following the **Red → Green → Refactor** loop,
these criteria should be written as failing tests first.

**Copilot outputs:**

- Given/When/Then for the happy path
- negative cases:
  - auth/permission
  - validation failures
  - empty state
  - partial failure / retry
  - timeouts/network error
  - concurrency/idempotency where relevant

**TDD integration:**

- Each acceptance criterion maps to one or more test cases
- Tests are written **before** implementation (Red phase)
- Criteria must be specific enough to produce deterministic, automated tests
- Use AAA structure (Arrange-Act-Assert) when translating to tests

**Gate:** negative cases must be explicit; otherwise they will be "found" in
production. Criteria that cannot be translated to automated tests are not
"ready."

______________________________________________________________________

### 5) Story readiness (DoR) → “Backlog hygiene”

**Goal:** prevent engineering churn caused by incomplete stories.

**Copilot checks:**

- Success metric present?
- Dependencies identified?
- UX states defined (loading/empty/error)?
- Data implications known (new fields, migrations, privacy)?
- Telemetry/observability expectations stated?
- Rollout constraints (feature flags, canary) noted?

**Gate:** failing DoR means it’s not schedulable.

______________________________________________________________________

### 6) Conversion to repo artifacts → “Issue Form-compliant output”

**Goal:** avoid format drift across issues.

**Copilot does:**

- outputs story content in the exact fields required by your Issue Form
- suggests labels (feature, ui, backend, a11y, needs-design, blocked)

**Gate:** the story must be “Issue Form ready” before it enters sprint planning.

______________________________________________________________________

## C. Where Copilot CLI / Coding Agent fits

This step is mostly content, but you can still use agents to **operationalize**
your system:

- Use the coding agent to generate and maintain:
  - Issue forms (YAML), prompt files, and instruction files via PRs (reviewed by
    you).
- Version custom agents as `.agent.md` files under `.github/agents/` to keep
  “story behavior” stable.

______________________________________________________________________

## D. Recommended custom agents for User Stories (keep it pragmatic)

Mirror the structure you used for Requirements and UI/UX: **one builder agent +
one gate agent**.

### 1) `story-builder.agent.md` (primary agent)

**Mission:** generate a high-quality, sliceable set of user stories from a
feature brief.

**Non-negotiables:**

- produce multiple slices (not one mega story)
- enforce INVEST and include open questions
- output in Issue Form-friendly structure
- include explicit out-of-scope

### 2) `story-quality-gate.agent.md` (review/gate agent)

**Mission:** reject weak stories and propose precise rewrites.

**Non-negotiables:**

- verify INVEST + 3Cs completeness
- verify AC quality + negative cases
- verify DoR readiness for scheduling
- identify contradictions and hidden dependencies

### Optional skills (extra modularity)

- `gherkin-writer` — BDD Given/When/Then generation
- `edge-case-enumerator` — systematic negative cases per feature type
- `issue-form-normalizer` — converts free text into strict Issue Form sections

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store in `.github/prompts/` and invoke with `/...` in chat:

- `/story-candidates-from-brief` → generate journey + multiple story slices
- `/invest-check-and-rewrite` → validate INVEST; rewrite failing stories
- `/3cs-completion` → add conversation questions + confirmation
- `/bdd-acceptance-criteria` → Given/When/Then + negative cases
- `/dor-check` → DoR checklist pass + missing info
- `/issue-form-output` → produce Issue Form-compliant final output

______________________________________________________________________

## Example prompt file skeleton (story candidates)

```markdown
---
name: story-candidates-from-brief
description: Generate a sliceable set of user stories (INVEST) from a feature brief
---

Input: ${input:brief:Paste the feature brief}

Rules:
- Output 3–10 stories mapped to a user journey.
- Each story must be INVEST and include explicit value.
- Include assumptions and open questions.
- Include out-of-scope for the epic.
- Do not invent system facts; call out unknowns.

Output format:
- Epic summary
- Story list (ID, Title, As a/I want/So that)
- Notes: assumptions, open questions, out-of-scope
```

______________________________________________________________________

## Next step suggestion

The following artifacts are now available in this repository:

- `.github/agents/story-builder.agent.md` ✅ With issue template integration
- `.github/agents/story-quality-gate.agent.md` ✅
- `.github/prompts/story-to-issue-form.prompt.md` ✅ Converts story to issue form
  format
- `.github/ISSUE_TEMPLATE/02-user-story.yml` ✅ Issue form with required fields +
  DoR checklist
- `.github/copilot-instructions.md` ✅ With INVEST, DoR, and output format rules
- `.github/instructions/issue-output.instructions.md` ✅ Path-specific formatting
  rules

### Workflow Summary

```
@requirements ──handoff──> @story-builder ──handoff──> @story-quality-gate
                                │                              │
                                │                              ▼
                                │                        Validated story
                                │                              │
                                ▼                              │
                     /story-to-issue-form  <───────────────────┘
                                │
                                ▼
                     02-user-story.yml (GitHub Issue Form)
                                │
                                ▼
                         Backlog item
```
