# Building Custom GitHub Copilot Agents for the Full SDLC (Offline‑First)

This document summarizes best practices for designing **multiple custom GitHub
Copilot agents** (one per SDLC stage) that work across **VS Code**, **Copilot
CLI**, and the **Copilot Coding Agent**, with a strong bias toward
**offline-first** workflows.

> Scope assumptions: Solo developer; Python backend + JavaScript/TypeScript
> frontend; git-based workflow.

______________________________________________________________________

## Executive Summary

Modern GitHub Copilot supports **custom agents** (specialized AI personas
defined by YAML/Markdown profiles) that can automate tasks across the software
development lifecycle (SDLC). The most scalable operating model is **modular,
multi-agent**:

- **One agent per SDLC stage** (requirements → architecture → coding → testing →
  docs → deployment → maintenance).
- **Tight tool-scoping per agent** (least-privilege tools; avoid accidental
  edits).
- **Composable workflows** using:
  - **Handoffs** (explicit “next-step” transitions between agents)
  - **Skills** (reusable instruction packs/templates/scripts that auto-load when
    relevant)

Store agent files at repo and/or user scope so they are discoverable by VS Code
Chat and Copilot CLI.

______________________________________________________________________

## Core Best Practices

### 1) Design for Modularity and Handoffs

Use a multi-agent “assembly line” model:

- **Requirements agent** produces acceptance criteria and non-functional
  requirements.
- **Architecture agent** produces design artifacts and module breakdown.
- **Implementation agent(s)** produce code changes.
- **Testing agent** produces tests and coverage improvements.
- **Docs agent** produces README/API docs and user guides.
- **Deployment agent** produces CI/CD and release artifacts.
- **Maintenance agent** produces refactors and dependency hygiene.

**Handoffs** reduce context sprawl and enforce stage boundaries: each agent gets
only the context it needs.

### 2) Least-Privilege Tooling

For each agent profile, explicitly control `tools:`:

- Planning/design agents: `read`, `search`, `edit` (docs only)
- Testing agent: `read`, `edit`, `shell` (tests + runners), avoid production
  edits
- Coding agent: `read`, `edit`, `shell` (build/test), allow production edits
- Deployment agent: `read`, `edit`, `shell` (build/deploy tooling)

Avoid enabling everything by default—treat tools as permissions.

### 3) Repo-Level + User-Level Agent Strategy

Use both scopes:

- **Repo-level** for project-specific conventions: `.github/agents/*.agent.md`
- **User-level** for global patterns: `~/.copilot/agents/*.agent.md`

This allows cross-repo reuse while keeping per-project nuances in-repo.

### 4) Git as the Spine of the Workflow

Make git the canonical source of truth:

- Use branches/commits as “checkpoints”
- Require tests to pass before merges
- Encourage the coding agent to:
  - make small commits
  - write descriptive messages
  - keep diffs reviewable
- Treat agent output as PR-ready (even as a solo developer)

### 5) Offline-First: Optimize for Local Context + Local Tools

Offline-first is practical for most SDLC work if you can:

- run tests locally
- access local docs
- use local linting/formatting
- run local build tools (Python + Node toolchains)

Where internet is required, isolate those steps (see Offline vs Online section).

______________________________________________________________________

## SDLC Agents: What Each Agent Should Do

### Requirements Gathering Agent

**Goal:** turn informal ideas into structured requirements.

- Inputs: issue text, user stories, local docs
- Outputs: acceptance criteria, constraints, edge cases, non-functional
  requirements
- Tools: `read`, `search`, `edit` (avoid code changes)

**Offline:** works well using local documents and existing repo context.
**Online-only use cases:** web research, standards lookups, competitor analysis.

______________________________________________________________________

### Architecture Design Agent

**Goal:** propose system structure and interfaces.

- Outputs:
  - module boundaries
  - data model / API contracts
  - key flows and failure modes
  - milestones / implementation sequencing
- Tools: `read`, `search`, `edit` (optional `shell` for diagram tooling)

**Offline:** can generate diagrams and architecture docs using local context.
**Online-only use cases:** fetching external architecture references, cloud
service docs.

______________________________________________________________________

### Coding / Implementation Agent(s)

**Goal:** write code changes safely and incrementally.

Recommended split (at minimum):

- **Backend agent (Python)**: frameworks, style, typing, tests
- **Frontend agent (JS/TS)**: TypeScript discipline, lint rules, UI patterns

Tools: `read`, `edit`, `shell` (build/test/lint), plus git operations via shell.

**Offline:** strong, as long as you have local models and local toolchains.
**Online-only use cases:** using cloud-run coding agent; accessing hosted APIs
or remote environments.

______________________________________________________________________

### Testing Agent

**Goal:** improve quality gates and reduce regressions.

- Outputs:
  - unit/integration/e2e tests as applicable
  - coverage improvements
  - test data/fixtures
- Tools: `read`, `edit`, `shell` (pytest, npm test, playwright, etc.)
- Policy: avoid editing production code unless explicitly permitted

**Offline:** excellent (local test runners). **Online-only use cases:** if CI
pipelines or remote test environments are required.

______________________________________________________________________

### Documentation Agent

**Goal:** keep docs accurate and usable.

- Outputs:
  - README updates
  - API docs / examples
  - usage guides / troubleshooting
  - code comments/docstrings (selectively)
- Tools: `read`, `edit` (optionally `search`)

**Offline:** strong (local codebase is primary source). **Online-only use
cases:** linking to external references; style guide lookups.

______________________________________________________________________

### Deployment / DevOps Agent

**Goal:** packaging, CI/CD, releases.

- Outputs:
  - Dockerfiles, compose files
  - GitHub Actions workflows
  - deployment scripts and runbooks
- Tools: `read`, `edit`, `shell`

**Offline:** building artifacts and validating configs works. **Online-only use
cases:** pushing images, deploying to cloud, running remote CI, creating
releases.

______________________________________________________________________

### Maintenance Agent

**Goal:** ongoing hygiene and evolution.

- Outputs:
  - refactors
  - dependency upgrades (Python + Node)
  - performance improvements
  - security remediation
- Tools: `read`, `edit`, `search`, `shell`

**Offline:** static analysis and refactors work well. **Online-only use cases:**
CVE feeds, upstream changelogs, remote dependency metadata.

______________________________________________________________________

## Extensibility and Control Plane

### Agent Profiles

Define each agent in an `.agent.md` file with:

- identity + mission
- tool permissions
- constraints and guardrails
- output formats (checklists, PR-ready summaries, etc.)

### Skills (Reusable Packs)

Use **skills** to standardize recurring practices:

- commit message conventions
- testing patterns
- architectural templates
- security checklists
- documentation templates

### MCP Servers (Optional)

If you later want agents to talk to external systems (GitHub issues/PRs,
internal APIs, etc.), MCP servers are the extensibility mechanism. In
offline-first mode, keep MCP optional and disabled by default.

______________________________________________________________________

## Security and Performance Considerations (Offline-First)

### Security

Offline inference reduces IP leakage risk because code stays local. Still:

- **Sandbox shell execution** (container/VM) if you grant `shell` tools.
- Avoid auto-approving commands in environments with access to secrets.
- Prefer least-privilege tools per agent.

### Performance

Local models may be less capable than frontier cloud models, but often “good
enough” for SDLC automation. Plan compute capacity for:

- large codebases (context management)
- test execution time
- LLM inference latency

______________________________________________________________________

## Offline vs Online Use Cases (Practical Matrix)

| Capability                       | Offline-Friendly | Cloud/Online Only |
| -------------------------------- | ---------------: | ----------------: |
| Local code analysis & edits      |               ✅ |                   |
| Local tests/builds/linting       |               ✅ |                   |
| git commits/branches locally     |               ✅ |                   |
| Push/pull to remote repo         |                  |                ✅ |
| CI/CD (hosted runners)           |                  |                ✅ |
| Web research / live docs lookup  |                  |                ✅ |
| External APIs (live calls)       |                  |                ✅ |
| “Coding agent” on GitHub Actions |                  |                ✅ |

______________________________________________________________________

## Appendix: Starter Agent Templates (Minimal)

> These are intentionally minimal. Add your repo conventions in a shared
> `copilot-instructions.md` or a “skill” pack.

### A) Requirements Agent (`.github/agents/requirements.agent.md`)

```yaml
---
name: requirements
description: Turn ideas/issues into scoped requirements and acceptance criteria.
tools: ["read", "search", "edit"]
---

# Role
You are the Requirements Analyst.

# Objectives
- Produce clear, testable acceptance criteria.
- Identify edge cases and non-functional requirements.
- Avoid implementation details unless asked.

# Output format
- Problem statement
- User stories
- Acceptance criteria
- Risks/assumptions
```

### B) Architecture Agent (`.github/agents/architecture.agent.md`)

```yaml
---
name: architecture
description: Produce architecture, module boundaries, and interfaces.
tools: ["read", "search", "edit"]
---

# Role
You are the Software Architect.

# Objectives
- Propose components, data flows, and API contracts.
- Produce implementation milestones.

# Output format
- Components
- Data model
- APIs/interfaces
- Sequence/milestones
```

### C) Testing Agent (`.github/agents/testing.agent.md`)

```yaml
---
name: testing
description: Write tests and improve coverage. Avoid production code edits unless requested.
tools: ["read", "edit", "shell"]
---

# Role
You are the Test Engineer.

# Constraints
- Prefer modifying only test directories unless asked.
- Run tests locally and report failures.

# Output format
- New/updated tests
- Commands executed
- Coverage notes
```

______________________________________________________________________

## References (non-exhaustive)

- GitHub Docs: Custom Copilot agents, tools scoping, repo/user-level placement
- GitHub Copilot changelog: CLI SDK, Agent Skills
- Microsoft AI Toolkit: local model workflows for offline use
