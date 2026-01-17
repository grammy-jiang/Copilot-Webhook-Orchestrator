# Implementation Stage: Copilot Accelerates Coding/Refactoring; CI Enforces the Quality Floor (Practical + Repeatable)

If you want Copilot to raise implementation quality (not just output more code),
you need **two control planes**:

1. **Agent discipline**: Copilot generates changes in small, test-backed
   increments.
1. **System discipline**: branch protections/rulesets + required checks make
   quality non-negotiable.

______________________________________________________________________

## A. Baseline setup (so Copilot can’t bypass quality)

### 1) Repo instructions = “coding policy”

- Put repo-wide rules in `.github/copilot-instructions.md` and
  file/path-specific rules in `.github/instructions/*.instructions.md`. Avoid
  conflicting rules to reduce unpredictable behavior.
- Use `AGENTS.md` for governance and boundaries (what an agent may touch; what
  requires human approval).
- Define custom agent profiles under `.github/agents/*.agent.md` (Markdown +
  YAML frontmatter).

**Non-negotiables to encode**

- Small PRs, minimal diffs, and “no drive-by refactors.”
- Tests required for behavior changes.
- No new deps unless explicitly requested.
- No secrets; no logging of sensitive data.
- Adhere to your format/lint/type-check rules (CI is the source of truth).

### 2) CI as the “quality floor” (hard enforcement)

Use branch protection or rulesets to require:

- **PR required** before merge
- **Required status checks** (lint/format/typecheck/tests)
- Optional: **code scanning results** and other quality signals Also consider
  CODEOWNERS + required approvals for sensitive areas.

### 3) Security + dependency governance (CI-level)

- Add Dependency Review to PRs and treat it as a required status check (block
  merges if vulnerable dependencies are introduced).
- If you run CodeQL scanning, incorporate scanning results into the merge gate.

______________________________________________________________________

## B. Implementation workflow with Copilot embedded (end-to-end)

### 1) Task intake → “Implementation plan with constraints”

**You provide**

- link to story/spec/contract (OpenAPI, schema, ADR)
- scope boundaries + non-goals
- definition of done (tests, observability, rollout)

**Copilot outputs**

- a short implementation plan: files to touch, risks, test strategy, rollback
  note

**Gate:** if it can’t name test changes + edge cases, it’s not ready to code.

______________________________________________________________________

### 2) “Scaffold → implement → harden” (three-pass loop)

**Pass 1 — scaffold**

- generate minimal structure (routes, handlers, components, types) aligned with
  repo patterns

**Pass 2 — implement**

- implement the happy path + deterministic behavior
- keep changes tight (avoid broad refactors)

**Pass 3 — harden**

- add error handling, input validation, retries/timeouts where appropriate
- add logs/metrics hooks (at least consistent logging)

**Gate:** every pass must keep CI green (or explicitly explain why not yet).

______________________________________________________________________

### 3) Test-Driven Development (TDD) Loop (Non-Negotiable for Behavior Changes)

Implementation follows the **Red → Green → Refactor** cycle:

#### Red Phase: Write a Failing Test First

- Write ONE test for the next small behavior
- Run it and confirm it fails for the **right reason**
- Test must be deterministic (no random, no real time, no external calls)

#### Green Phase: Implement Minimal Code

- Write the **smallest change** that makes the test pass
- No over-engineering; no premature optimization
- Stay focused on the failing test

#### Refactor Phase: Improve Structure

- Remove duplication
- Clarify naming
- Improve design
- **All tests must stay green**

**Test coverage requirements:**

- ✅ Happy path
- ✅ Permission/auth failures
- ✅ Validation failures
- ✅ Empty/null states
- ✅ Typical operational failures (timeouts/network/DB)

**Test design rules (from TDD best practices):**

- **Behavior over implementation**: verify *what* the system does, not *how*
- **Single responsibility per test**: one behavior/branch per test
- **AAA structure**: Arrange → Act → Assert in every test
- **Independent tests**: can run in any order; no hidden coupling
- **Mock boundaries only**: mock HTTP/DB/external services, not internal
  functions

**Gate:** "no tests, no merge" for behavior changes. Tests written *after* code
is a red flag.

______________________________________________________________________

### 4) Refactoring with guardrails (safe refactor play)

Use Copilot for refactors only when you enforce:

- refactor in isolated commits
- preserve behavior; tests demonstrate equivalence
- measurable wins (complexity reduction, duplication removal, perf budget)

**Gate:** refactor PRs must be smaller than feature PRs, or they get rejected.

______________________________________________________________________

### 5) PR packaging (make review cheap)

Even if you’ll have a separate code-review stage, implementation should produce:

- PR description: what/why, tradeoffs, test evidence
- screenshots or storybook/demo links (frontend)
- migration/rollback note (backend)

**Gate:** reviewers should not have to reverse-engineer intent.

______________________________________________________________________

## C. Where Copilot CLI / Coding Agent fits (high leverage)

### 1) Copilot coding agent for multi-file tasks (PR-based)

Use the coding agent when you want a coherent multi-file change set with a PR
outcome.

### 2) Terminal-driven delegation

If you prefer terminal workflows, use Copilot CLI to delegate tasks and bring
back a PR/diff for review.

**Governance model**

- agent generates a branch + PR → CI runs → human approves/merges
- CI gates are the real enforcement, not agent promises

______________________________________________________________________

## D. Recommended custom agents for Implementation (pragmatic set)

Mirror your earlier pattern: **one builder agent + one gate agent**.

### 1) `implementation-driver.agent.md` (primary agent)

**Mission:** implement features quickly but safely, aligned with repo
conventions.

**Non-negotiables**

- work in small commits and small PR scope
- follow contracts/specs; don’t invent APIs
- update/add tests for behavior changes
- no new dependencies unless requested
- produce PR evidence (tests run, screenshots where relevant)

### 2) `ci-quality-gate.agent.md` (gate agent)

**Mission:** treat CI as a policy engine; fix failures with minimal diffs.

**Non-negotiables**

- do not “paper over” failing tests; fix root cause
- keep formatting/lint fixes separate from logic changes when possible
- preserve backward compatibility unless the spec explicitly breaks it
- escalate when failures indicate missing requirements or bad contracts

### Optional specialist agents (only if you feel pain)

- `refactor-surgeon` — refactor-only PRs with strict safety rails
- `test-accelerator` — test coverage + edge-case expansion
- `dependency-hygiene` — dependency bumps + license/vuln governance

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store these in `.github/prompts/` and invoke via `/...`:

- `/implement-from-spec` → implement strictly from story/spec/contracts; propose
  file plan + tasks
- `/scaffold-minimal` → generate skeleton only (no business logic)
- `/add-tests-for-change` → generate/update tests + edge cases
- `/refactor-safely` → refactor plan + staged commits + safety constraints
- `/fix-ci-failures` → minimal-diff fixes based on CI logs
- `/pr-evidence-pack` → PR summary + test evidence + screenshots checklist

______________________________________________________________________

## Example prompt file skeleton (CI fix loop)

```markdown
---
name: fix-ci-failures
description: Fix CI failures with minimal diffs and no scope creep
agent: ci-quality-gate
tools: [workspace]
---

Input:
1) ${input:ci_log:Paste CI log snippets}
2) ${input:context:What changed + link to spec}

Rules:
- Minimal diffs. Do not refactor unrelated code.
- Prefer fixing logic over weakening checks.
- Keep formatting-only changes separate if feasible.
- If failure indicates spec ambiguity, stop and list the exact missing requirement(s).

Output:
- Root cause analysis (short)
- Proposed patch plan (files + edits)
- Tests to add/update (if needed)
```

______________________________________________________________________

## Next step suggestion

If you want to keep going one-by-one, the next concrete deliverable is to
generate repo-ready artifacts:

- `.github/agents/implementation-driver.agent.md`
- `.github/agents/ci-quality-gate.agent.md`
- 6 prompt files under `.github/prompts/`
- A reference CI gate checklist aligned with your branch protections/rulesets
  (required checks)
