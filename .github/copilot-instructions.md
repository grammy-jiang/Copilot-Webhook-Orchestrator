# Copilot Instructions

This file provides repository-wide instructions for GitHub Copilot.
These rules apply to all Copilot interactions (VS Code Chat, Coding Agent).

______________________________________________________________________

## Project Context

This is an **agentic development template** repository containing:

- Custom GitHub Copilot agents (`.github/agents/*.agent.md`)
- Skills for reusable behaviors (`.github/skills/*/SKILL.md`)
- Best practices documentation (`docs/best_practices/`)
- Issue templates for structured backlog management (`.github/ISSUE_TEMPLATE/`)

The project follows an **agent-driven SDLC** with distinct lifecycle stages:
Requirements → Architecture → UI/UX → Implementation → Testing → Review → Release/Ops

______________________________________________________________________

## Issue Template Integration

When generating content that will become a GitHub Issue, output in a format
compatible with our Issue Templates located in `.github/ISSUE_TEMPLATE/`.

### Available Issue Templates

| Template | Use When | Key Fields |
|----------|----------|------------|
| `01-feature-request.yml` | Proposing new features | Problem, Solution, Success Metrics, Constraints |
| `02-user-story.yml` | Creating backlog stories | User Story, AC (happy + edge), DoR Checklist, Out of Scope |
| `03-bug-report.yml` | Reporting bugs | Current/Expected Behavior, Repro Steps, Environment |
| `04-architecture-decision.yml` | Documenting ADRs | Context, Options, Decision, Consequences |
| `05-technical-debt.yml` | Tracking tech debt | Description, Risk Level, NFR Impact, Refactor Scope |
| `06-test-case-gap.yml` | Missing test coverage | Related Story, Untested AC, Proposed Tests |
| `07-release-request.yml` | Requesting releases | Version, Changelog, Rollback Plan, Monitoring |
| `08-incident-report.yml` | Post-incident reviews | Timeline, Root Cause, Impact, Action Items |

### Output Format Rules

When asked to generate a user story, feature request, bug report, ADR, or similar:

1. **Structure output to match the corresponding Issue Template fields**
1. **Include all required fields** (marked with `required: true` in the template)
1. **Use the exact field names** from the template for easy copy-paste
1. **Do not invent fields** that don't exist in the template

______________________________________________________________________

## User Story Standards (INVEST)

All user stories MUST satisfy **INVEST** criteria:

- **I**ndependent: Can be developed without blocking or being blocked
- **N**egotiable: Captures intent, not implementation details
- **V**aluable: Delivers clear business or user value
- **E**stimable: Small and clear enough to estimate
- **S**mall: Completable within one iteration (1-2 weeks max)
- **T**estable: Has verifiable acceptance criteria

### Acceptance Criteria Format

Use **Given/When/Then** (Gherkin) format:

```gherkin
Scenario: [Name]
  Given [initial context]
  When [action is performed]
  Then [expected outcome]
```

**Always include edge cases:**

- Empty/null/missing data states
- Permission/authorization failures
- Validation failures
- Network/timeout errors
- Concurrency/idempotency (where applicable)

______________________________________________________________________

## Definition of Ready (DoR)

A story is NOT ready for implementation until:

- [ ] User value is clearly stated
- [ ] Success metric is defined (quantified when possible)
- [ ] Acceptance criteria are complete (happy path + edge cases)
- [ ] Dependencies are identified
- [ ] Out of scope is explicitly listed
- [ ] Data model impact is assessed
- [ ] Security/privacy implications are reviewed
- [ ] UX states are defined (loading, empty, error)

______________________________________________________________________

## Code Generation Standards

### General Rules

- Follow existing patterns in the codebase
- Prefer small, focused changes over large refactors
- Include tests for behavior changes
- No secrets or sensitive data in code
- No new dependencies without explicit request

### Test-Driven Development (TDD)

When implementing features:

1. **Red**: Write a failing test first
1. **Green**: Write minimal code to pass the test
1. **Refactor**: Improve structure while keeping tests green

Tests must be:

- **Deterministic**: Fixed clocks, seeded randomness, hermetic fixtures
- **Behavioral**: Test user-visible outcomes, not implementation details
- **Layered**: Unit (many, fast) → Integration (some) → E2E (few, critical paths)

______________________________________________________________________

## Documentation Standards

- Use Markdown for all documentation
- Include Mermaid diagrams for architecture and flows
- Keep docs co-located with code when possible
- Update docs when behavior changes

______________________________________________________________________

## Agent Handoff Context

When handing off to another agent, include:

1. **What was done**: Summary of completed work
1. **Current state**: What exists now
1. **What's needed next**: Specific ask for the receiving agent
1. **Open questions**: Unresolved issues to address

______________________________________________________________________

## Checkpoint Resume Protocol

Agents save checkpoint files with a YAML frontmatter header for resumption. When a user asks to "resume" or "continue" work from a file or folder, follow this protocol:

### Checkpoint File Format

All checkpoint files include this frontmatter:

```yaml
---
checkpoint:
  agent: <agent-name>           # Agent that created this checkpoint
  stage: <lifecycle-stage>      # Requirements | Architecture | UI/UX | Implementation | Testing | Review | Release/Ops
  status: <status>              # complete | in-progress | blocked
  created: <ISO-date>
  next_agents:                  # Recommended agents to continue with
    - agent: <agent-name>
      action: <what to do>
    - agent: <agent-name>
      action: <what to do>
---
```

### Resume Routing Rules

When user asks to resume from checkpoint files:

1. **Read the checkpoint frontmatter** to identify the source agent and next agents
2. **Check the status**:
   - `complete` → Route to one of the `next_agents`
   - `in-progress` → Continue with the same `agent`
   - `blocked` → Show the blocker and ask user for resolution
3. **Invoke the appropriate agent** with context from the checkpoint files

### Checkpoint Location Mapping

| Folder Pattern | Source Agent | Typical Next Agents |
|----------------|--------------|---------------------|
| `docs/requirements/<feature>/` | `requirements` | `story-builder`, `arch-spec-author` |
| `docs/stories/<feature>/` | `story-builder` | `story-quality-gate`, `arch-spec-author` |
| `docs/architecture/<feature>/` | `arch-spec-author` | `risk-and-nfr-gate`, `implementation-driver` |
| `docs/ui/<feature>/` | `ui-scaffolder` | `a11y-guardian`, `test-drafter` |
| `docs/testing/<feature>/` | `test-drafter` | `implementation-driver`, `test-truth-and-stability-gate` |
| `docs/implementation/<feature>/` | `implementation-driver` | `code-reviewer`, `test-drafter` |
| `docs/releases/<version>/` | `release-pipeline-author` | `prod-risk-and-rollback-gate`, `runbook-and-ops-docs` |
| `docs/runbooks/<feature>/` | `runbook-and-ops-docs` | `incident-scribe` |
| `docs/incidents/<incident-id>/` | `incident-scribe` | `story-builder` |

### Example Resume Flow

**User says:** "Resume work from `docs/requirements/user-auth/`"

**Copilot should:**
1. Read `docs/requirements/user-auth/one-pager.md`
2. Parse the checkpoint frontmatter
3. If status is `complete`, offer: "The requirements are complete. Would you like me to invoke `@story-builder` to create user stories, or `@arch-spec-author` to design the architecture?"
4. If status is `in-progress`, invoke `@requirements` to continue

______________________________________________________________________

## References

- Lifecycle docs: `docs/best_practices/web-dev-lifecycle/`
- Agent definitions: `.github/agents/`
- Issue templates: `.github/ISSUE_TEMPLATE/`
- Skills: `.github/skills/`
