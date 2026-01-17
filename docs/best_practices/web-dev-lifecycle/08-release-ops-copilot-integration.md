# Release & Operations: Copilot Generates Pipelines/Scripts/Docs; You Manage Production Risk + Rollback (Practical + Repeatable)

If you want AI assistance without outsourcing accountability, treat production
as a **controlled environment** with **hard gates**. Copilot can draft the
machinery; **your job is risk ownership** (blast radius, rollback,
observability, and change control).

______________________________________________________________________

## A. Baseline setup (so production safety is systemic)

### 1) Branch governance = “quality floor”

Use GitHub rulesets/branch protections to make it impossible to merge/deploy
without guardrails:

- Require a pull request before merging
- Require status checks to pass
- Require code scanning / code quality results (if you use them)

This ensures ops automation never bypasses engineering discipline.

### 2) Deployment gates = “humans approve production”

Use GitHub Actions **environments** for production gating:

- Required reviewers (human approval to proceed)
- Prevent self-review (deployer cannot approve their own deployment)
- Wait timers (cooldown window)
- Optionally: custom deployment protection rules

This is the cleanest way to embed human-in-the-loop into the pipeline without
inventing your own tooling.

### 3) Secrets and identity = “no long-lived cloud keys”

- Use environment/repo secrets properly (prefer environment secrets for prod).
- Prefer **OIDC** for cloud auth so you don’t store long-lived cloud credentials
  as GitHub secrets; use short-lived tokens per job.

### 4) Standardize workflows = “reusable workflows as a platform”

Create reusable GitHub Actions workflows to standardize build/deploy patterns:

- `workflow_call` enables reusability; call via `jobs.<id>.uses`
- Prefer pinning by commit SHA for stability/security (where practical)

______________________________________________________________________

## B. Release/Ops workflow with Copilot embedded (end-to-end)

### 1) Release planning → “release intent + risk register”

**You provide**

- What’s changing (feature flag? schema change? infra change?)
- Risk posture (blast radius, user impact, dependencies)
- Rollback constraints (data migrations, irreversible actions)

**Copilot drafts**

- Release plan (steps, sequencing, owners)
- Risk register + mitigations
- Rollback plan + decision triggers (“if metric X breaches, rollback”)

**Gate:** if rollback isn’t credible, you’re not ready to ship.

______________________________________________________________________

### 2) Pipeline generation → “build once, deploy many”

**Copilot drafts**

- GitHub Actions workflow YAML(s): build, test, package, deploy
- Artifact/versioning strategy
- Reusable workflow extraction (if you have multiple repos/services)

**You enforce**

- Separation of concerns: build/test must complete before deploy
- Promotions: dev → staging → prod (prod requires environment approval) **CI
  pipeline phases (from TDD best practices):**

1. **Format + Lint** (fast fail)
1. **Unit tests** (high coverage, core modules ≥95%)
1. **Smoke tests** (quick system sanity)
1. **E2E tests** (critical journeys; strong artifacts)
1. **Security scans** (dependency review, CodeQL)
1. **Build + Package** (artifact creation)
1. **Deploy** (progressive: dev → staging → prod)

**Quality gates for merge:**

- Phases 1–4 must pass before PR merge
- No flaky tests tolerated in mainline
- Coverage reports and test artifacts published

______________________________________________________________________

### 3) Deployment strategy → “reduce blast radius”

**Copilot drafts**

- Canary/blue-green rollout steps
- Feature-flag rollout plan
- Verification checks (smoke, synthetic checks, health endpoints)

**You enforce**

- Progressive delivery defaults; big-bang releases are exceptions
- Clear “stop-the-line” thresholds

______________________________________________________________________

### 4) Observability & runbooks → “operability is part of the feature”

**Copilot drafts**

- Runbook template: symptoms → diagnosis → mitigations → rollback
- On-call notes: dashboards, key logs/metrics, common failure modes
- Post-deploy checklist

**You enforce**

- Runbooks must be executable (commands, links, known-good baselines)
- Alerts must be actionable (not spam)

______________________________________________________________________

### 5) Incident & postmortem docs → “AI can write, but cannot know the facts”

**Copilot drafts**

- Incident timeline structure
- Postmortem skeleton (root cause, contributing factors, corrective actions)

**You enforce**

- Facts must be verified; no invented timelines
- Action items must be measurable and owned

______________________________________________________________________

## C. Where custom agents fit (high leverage)

For release/ops you want **builders** and **gates**:

- Builders draft workflows/scripts/docs quickly.
- Gates block unsafe changes by demanding rollback credibility, blast-radius
  control, and environment approvals.

______________________________________________________________________

## D. Recommended custom agents for Release & Ops (pragmatic set)

### 1) `release-pipeline-author.agent.md` (builder)

**Mission:** generate CI/CD workflows, scripts, and docs aligned to your
platform standards.

**Non-negotiables**

- Use environments for prod gating (required reviewers, prevent self-review)
- Prefer OIDC for cloud auth; minimize long-lived secrets
- Produce reusable workflows when patterns repeat
- No “magic”: document assumptions and required manual steps

### 2) `prod-risk-and-rollback-gate.agent.md` (gate)

**Mission:** block unsafe releases by demanding rollback credibility and
blast-radius control.

**Non-negotiables**

- Explicit rollback plan + triggers required
- Identify irreversible actions (data deletes, schema breaks)
- Require canary/feature-flag strategy for high-risk changes
- Require environment approval for production

### 3) `runbook-and-ops-docs.agent.md` (builder)

**Mission:** generate runbooks, operational docs, and checklists.

**Non-negotiables**

- Commands are copy-pasteable
- Diagnostics reference real logs/metrics/dashboards (placeholders flagged
  explicitly)
- Include “what good looks like” baselines

### 4) `incident-scribe.agent.md` (assistant)

**Mission:** structure incident comms and postmortems.

**Non-negotiables**

- Never invent facts
- Mark missing timestamps/metrics as “unknown” placeholders
- Action items must have owner + due date + verification method

______________________________________________________________________

## E. Prompt file “command set” (what you actually run)

Store under `.github/prompts/` and invoke via `/...`:

- `/release-plan-from-change` → plan + risk register + rollback triggers
- `/generate-gh-actions-pipeline` → workflow YAML + environment gates
- `/secure-cloud-auth-with-oidc` → OIDC-based auth steps + minimal permissions
- `/extract-reusable-workflows` → convert repeated jobs to `workflow_call`
- `/runbook-for-deployment` → runbook + troubleshooting + rollback steps
- `/postmortem-skeleton` → structured postmortem doc (fact placeholders)

______________________________________________________________________

## Example prompt file skeleton (prod deployment with gates)

```markdown
---
name: generate-gh-actions-pipeline
description: Generate build/test/deploy workflows with production environment gates
agent: release-pipeline-author
tools: [workspace]
---

Input:
1) ${input:repo_context:Service type + stack + deploy target}
2) ${input:environments:dev/staging/prod definitions}
3) ${input:constraints:Rollback constraints, SLOs, security requirements}

Rules:
- Build once, deploy many: artifact promoted across envs.
- Production must use environment required reviewers + prevent self-review.
- Prefer OIDC over long-lived cloud secrets; request minimal permissions.
- If patterns repeat, propose reusable workflows with workflow_call.
- Output a rollback section with triggers.

Deliverables:
- .github/workflows/*.yml
- docs/release/RELEASE_PLAN.md
- docs/ops/RUNBOOK.md
```

______________________________________________________________________

## Next step suggestion

The following artifacts are now available in this repository:

- `.github/agents/release-pipeline-author.agent.md` ✅
- `.github/agents/prod-risk-and-rollback-gate.agent.md` ✅
- `.github/agents/runbook-and-ops-docs.agent.md` ✅
- `.github/agents/incident-scribe.agent.md` ✅
- `.github/copilot-instructions.md` ✅ With release and ops rules

### Issue Templates for Release & Ops Stage

| Template                 | Use When              | Key Fields                                                         |
| ------------------------ | --------------------- | ------------------------------------------------------------------ |
| `07-release-request.yml` | Requesting releases   | Version, Changelog, Rollback Plan, Monitoring, Deployment Strategy |
| `08-incident-report.yml` | Post-incident reviews | Timeline, Root Cause, Impact, Action Items, Lessons Learned        |
