# Review Stage: Copilot Pre-Review + Human Gate; Accountability Stays with Humans (Practical + Repeatable)

The objective is not “AI review replaces humans.” The objective is **shift-left
quality**: Copilot catches obvious defects early, while **branch governance +
human approvals** remain the merge gate.

______________________________________________________________________

## A. Baseline setup (so review quality is systemic, not optional)

### 1) Repo instructions = “review policy”

- Put review expectations in `.github/copilot-instructions.md` (what reviewers
  should look for; what authors must provide).
- Use `.github/instructions/*.instructions.md` for review-related docs/templates
  if you want tighter rules for PR templates/checklists than general code.
- Maintain `AGENTS.md` as governance: what your agents can touch, and what
  requires human approval.

### 2) Merge gate = branch protection / rulesets

Your “quality floor” should be enforced by GitHub, not by reviewer heroics:

- Require **pull requests** before merging
- Require **approving reviews**
- Require **status checks** (tests/lint/typecheck/security scanning)
- Optionally require conversation resolution, signed commits, linear history,
  merge queue, etc.

### 3) CODEOWNERS = targeted human responsibility

Use `CODEOWNERS` for “domain ownership,” and (where relevant) require review
from code owners as part of protected-branch settings.

**Bottom line:** Copilot can pre-review everything; humans remain accountable
for approvals.

______________________________________________________________________

## B. Review workflow with Copilot embedded (end-to-end)

### 1) Author-side “pre-review” (before opening PR)

**Goal:** reduce reviewer load and prevent avoidable back-and-forth.

**Copilot does**

- Runs a structured pre-review using a prompt file (e.g., `/review-code`) to
  produce a comprehensive report: security, performance, quality, design,
  testing, docs.
- Produces a **PR readiness pack**:
  - risk hotspots
  - “what I tested” evidence
  - suggested reviewer focus areas
  - known limitations/open questions

**Human gate (you)**

- Validate that the report ties back to spec/contracts and that the PR has real
  test evidence (not “looks fine”).

______________________________________________________________________

### 2) PR creation with structured metadata

**Goal:** force clarity.

**Copilot does**

- Drafts PR description: what/why, tradeoffs, screenshots, test steps
- Drafts reviewer checklist aligned to your repository standards

**Human gate**

- Ensure no scope creep and that the change matches the story/spec.

______________________________________________________________________

### 3) Human review gate (the real decision point)

**Goal:** correctness and risk control, not formatting.

**Review focus areas**

- Logic correctness + edge cases
- Security and permissions model
- Error handling + observability (logs/metrics)
- Data integrity + migrations
- Maintainability + test quality

**Enforcement**

- Required reviewer approvals and required checks must be green before merge.

______________________________________________________________________

### 4) Comment resolution loop (AI-assisted, human-owned)

**Copilot does**

- Converts review comments into a fix plan
- Implements small, mechanical changes (refactors, typing, missing tests) with
  minimal diffs
- Keeps fixes scoped to the review feedback (no opportunistic rewrites)

**Human gate**

- Confirm the fix actually addresses the concern (not just silences CI).
- Re-run pre-review if the changes are non-trivial.

______________________________________________________________________

## C. Where custom agents fit (high leverage in review)

You want **two roles**:

1. **Pre-review agent (AI)**: produces a structured report and PR readiness
   artifacts.
1. **Gate agent (human policy proxy)**: enforces that merge criteria are met,
   but does **not** “approve” on your behalf.

______________________________________________________________________

## D. Recommended custom agents for Review (pragmatic set)

### 1) `pr-pre-reviewer.agent.md` (primary agent)

**Mission:** generate a high-signal pre-review report *before* human review time
is spent.

**Non-negotiables**

- Use the same review taxonomy every time: Security / Perf / Quality / Design /
  Testing / Docs
- Produce a “PR readiness pack” (risk list + evidence + reviewer focus)
- No “confidence theater”: explicitly list unknowns and assumptions
- No dependency additions unless explicitly allowed

### 2) `review-comment-fixer.agent.md` (execution agent)

**Mission:** implement reviewer feedback with minimal diffs and strong tests.

**Non-negotiables**

- No unrelated refactors
- Fix root causes (don’t weaken checks)
- Update/add tests when behavior changes
- Preserve contracts/specs

### 3) `merge-readiness-auditor.agent.md` (gate-support agent)

**Mission:** produce a merge readiness report (CI status + checklist) but never
“approves.”

**Non-negotiables**

- Summarize required checks + their status
- Confirm CODEOWNERS requirements are met (if configured)
- Highlight unresolved conversations / missing evidence

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store in `.github/prompts/` and invoke via `/...`:

- `/review-code` → comprehensive review report
- `/pr-readiness-pack` → PR description + risk list + test evidence checklist
- `/diff-risk-summary` → “what changed + what can break” shortlist
- `/review-comment-to-fix-plan` → convert comments into tasks + commit plan
- `/merge-readiness-report` → checklist-based readiness report (no approval)

______________________________________________________________________

## Example prompt file skeleton (pre-review pack)

```markdown
---
name: pr-readiness-pack
description: Produce a pre-review report + PR-ready metadata (no approvals)
agent: pr-pre-reviewer
tools: [workspace]
---

Input:
1) ${input:context:Link to story/spec + what changed}
2) ${input:focus:Optional focus areas (security/perf/testing)}

Rules:
- Output must include: Critical Issues / Suggestions / Good Practices.
- Tie issues to concrete files/lines where possible.
- Require test evidence: what was added/updated, and how to run it.
- List unknowns/assumptions explicitly. No fake certainty.
- Do NOT state that the PR is "approved" or "ready to merge".

Deliverables:
1) PR summary (what/why)
2) Risk hotspots + reviewer focus list
3) Test evidence checklist
4) Follow-up tasks (if any)
```

______________________________________________________________________

## Next step suggestion

If you want to proceed one-by-one, the next concrete deliverable is to produce:

- `.github/agents/pr-pre-reviewer.agent.md`
- `.github/agents/review-comment-fixer.agent.md`
- `.github/agents/merge-readiness-auditor.agent.md`
- 5 prompt files under `.github/prompts/_topics`
- A PR template and review checklist aligned with your required checks and
  branch protections
