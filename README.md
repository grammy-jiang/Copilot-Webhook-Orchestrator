# agentic-dev-template

AI-first GitHub template repository that standardizes specs, architecture notes,
guardrails, and CI quality gates so coding agents (e.g., Copilot) can ship
predictable changes with tests, reviews, and reproducible workflows.

## 📋 Overview

This repository provides a structured framework for AI-assisted software
development using GitHub Copilot. It combines traditional software development
best practices with modern AI-driven workflows, enabling faster, more reliable
feature delivery while maintaining code quality and architectural consistency.

______________________________________________________________________

## ✨ Features

- **Agent-driven SDLC:** Predefined Copilot agents map to each lifecycle stage
  with clear handoffs.
- **Issue templates:** Structured GitHub Issue Forms for features, stories,
  bugs, ADRs, release requests.
- **TDD-first workflow:** Integrated Red→Green→Refactor loops with testing gates
  and stability checks.
- **Architecture scaffolds:** Mermaid diagrams, OpenAPI contracts, and ADR
  guidance.
- **Quality gates:** Accessibility, security/NFR review, CI checks, and merge
  readiness audits.
- **Docs funnel:** Clear links to lifecycle guides, best practices, and
  contribution workflow.

## 🚀 How to Use This Template with GitHub Copilot

### The AI-Assisted Development Lifecycle

This template implements a **8-stage development lifecycle** where GitHub
Copilot agents support teams at each phase:

| Stage                 | Traditional Role                               | Copilot Support                                                | Key Output                                             | Issue Templates                                                  |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------- |
| **1. Requirements**   | Gather stakeholder needs, define value         | Draft user stories, acceptance criteria, risk analysis         | Feature specs, user stories with DoR                   | 📋 `01-feature-request.yml`<br/>📋 `02-user-story.yml`           |
| **2. UI/UX Design**   | Design user experience, create prototypes      | Scaffold components, generate mock data, accessibility audits  | Component code, design systems, A11y reports           | —                                                                |
| **3. Architecture**   | Specify system design, define contracts        | Generate diagrams, API specs, ADRs, threat models              | API contracts, architecture diagrams, security reviews | 📋 `04-architecture-decision.yml`<br/>📋 `05-technical-debt.yml` |
| **4. Implementation** | Write production code                          | Code generation, refactoring guidance, test-driven development | Production code following TDD (Red→Green→Refactor)     | 📋 `03-bug-report.yml`                                           |
| **5. Testing**        | Define test strategy, write tests              | Generate unit/integration/E2E tests, ensure coverage           | Test suites, coverage validation                       | 📋 `06-test-case-gap.yml`                                        |
| **6. Code Review**    | Review code quality, security, maintainability | Pre-review analysis, suggest improvements, fix feedback        | Merge-ready PRs, quality gates                         | —                                                                |
| **7. Release & Ops**  | Deploy, monitor, run operations                | Generate pipelines, runbooks, incident analysis                | CI/CD workflows, operational docs                      | 📋 `07-release-request.yml`<br/>📋 `08-incident-report.yml`      |

### Recommended Workflow Steps

#### 1️⃣ **Requirements Stage** → Draft & Validate Stories

```bash
# Start with a feature idea or problem statement
# Use VS Code Copilot Chat to:
# - Draft a feature one-pager with problem statement, success metrics, constraints
# - Generate INVEST-compliant user stories with Given/When/Then acceptance criteria
# - Identify edge cases, dependencies, and out-of-scope items
# - Produce a Definition of Ready (DoR) checklist

# Create GitHub Issue using 01-feature-request.yml or 02-user-story.yml template
```

**Key artifacts:**

- Feature requirements with success metrics
- User stories following
  [INVEST principles](docs/best_practices/web-dev-lifecycle/03-user-stories-copilot-integration.md)
- Acceptance criteria in Gherkin format (Given/When/Then)
- Risk register and non-functional requirements (NFRs)

______________________________________________________________________

#### 2️⃣ **UI/UX Design Stage** → Component & Design System

```bash
# Use VS Code Copilot Chat to:
# - Scaffold React/Vue/etc. components from design specs
# - Generate realistic mock data and test fixtures
# - Create Storybook stories for component documentation
# - Validate WCAG accessibility compliance
```

**Key artifacts:**

- Component scaffolds with TypeScript/JSX
- Mock data and fixtures
- Accessibility audit report
- Responsive design validation

See
[UI/UX Design Integration](docs/best_practices/web-dev-lifecycle/02-ui-ux-design-copilot-integration.md).

______________________________________________________________________

#### 3️⃣ **Architecture Stage** → Design System & Contracts

```bash
# Use VS Code Copilot Chat to:
# - Generate Mermaid/C4 diagrams (context, container, sequence)
# - Draft OpenAPI/JSON Schema API contracts
# - Create data models and migration strategies
# - Write Architecture Decision Records (ADRs)
# - Conduct threat modeling and security review
```

**Key artifacts:**

- Architecture diagrams (Mermaid/PlantUML)
- OpenAPI specifications with error models
- Data models and schemas
- Architecture Decision Records (ADRs)
- Security/threat analysis

See
[Spec & Architecture Integration](docs/best_practices/web-dev-lifecycle/04-spec-architecture-copilot-integration.md).

______________________________________________________________________

#### 4️⃣ **Implementation Stage** → Test-Driven Development (TDD)

```bash
# Follow Test-Driven Development (TDD) Red→Green→Refactor cycle:

# RED: Use test-drafter agent to write failing tests
# GREEN: Use implementation-driver agent to write minimal code
# REFACTOR: Improve code structure while keeping tests green

# Copilot CLI and Chat:
# - Generate unit tests for business logic
# - Refactor code safely with Copilot guidance
# - Use Copilot /explain to understand complex code
```

**Key practices:**

- Write failing tests first (Red)
- Implement minimal code to pass tests (Green)
- Refactor code while maintaining test coverage
- Enforce deterministic, hermetic tests

See
[Implementation Integration](docs/best_practices/web-dev-lifecycle/05-implementation-copilot-integration.md).

______________________________________________________________________

#### 5️⃣ **Testing Stage** → Quality & Coverage Gates

```bash
# Use VS Code Copilot Chat to:
# - Generate comprehensive unit/integration/E2E test suites
# - Suggest missing edge case scenarios (null checks, errors, timeouts)
# - Draft Playwright/Cypress E2E flows for critical user journeys
# - Ensure deterministic, stable test environments
```

**Key artifacts:**

- Unit tests (high coverage, fast execution)
- Integration tests (module boundaries)
- E2E tests (critical user journeys)
- Coverage reports and analysis

See
[Testing Integration](docs/best_practices/web-dev-lifecycle/06-testing-copilot-integration.md).

______________________________________________________________________

#### 6️⃣ **Code Review Stage** → Quality & Merge Gates

```bash
# Use Copilot as a "pre-reviewer":
# - Summarise diffs and highlight risks
# - Suggest refactors with rationale
# - Check for security, performance, maintainability issues
#
# Then request human code review via GitHub PR
# Use Copilot Coding Agent to implement review feedback
```

**Key practices:**

- Automated checks (lint, tests, SAST, dependency scanning)
- Copilot pre-review analysis
- Human two-eyes review gate
- Merge readiness audits

See
[Review Stage Integration](docs/best_practices/web-dev-lifecycle/07-review-stage-copilot-integration.md).

______________________________________________________________________

#### 7️⃣ **Release & Ops Stage** → Pipelines & Runbooks

```bash
# Use VS Code Copilot Chat to:
# - Generate CI/CD workflows (GitHub Actions, etc.)
# - Create Dockerfiles, Kubernetes manifests, Helm charts
# - Draft operational runbooks and incident response guides
# - Generate incident summaries and RCA templates
```

**Key artifacts:**

- CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
- Deployment configurations (Docker, Kubernetes)
- Operational runbooks and disaster recovery procedures
- Incident postmortem templates

See
[Release & Ops Integration](docs/best_practices/web-dev-lifecycle/08-release-ops-copilot-integration.md).

______________________________________________________________________

## 🔄 Iterative Loops & Feedback Loops

Development is not strictly linear. Quality gates and feedback from later stages
trigger refinement loops:

| Loop                         | Trigger                           | Flow                                                                               | Purpose                                                    |
| ---------------------------- | --------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Story Refinement**         | Quality issues in requirements    | `story-quality-gate` → `story-builder`                                             | Fix INVEST violations, incomplete acceptance criteria      |
| **Architecture Update**      | Risk/NFR gaps found               | `risk-and-nfr-gate` → `arch-spec-author`                                           | Address security/performance concerns before coding        |
| **Design Accessibility Fix** | A11y audit fails                  | `a11y-guardian` → `ui-scaffolder`                                                  | Ensure WCAG compliance before implementation               |
| **TDD Red→Green Cycle**      | Each behavior change (tight loop) | `test-drafter` (Red) → `implementation-driver` (Green) → `test-drafter` (Refactor) | Drive implementation with failing tests                    |
| **Test Coverage Gap**        | Coverage below threshold          | `test-truth-and-stability-gate` → `test-drafter`                                   | Add missing edge cases and scenarios                       |
| **Review Feedback Loop**     | Code review comments              | `code-reviewer` → `review-comment-fixer` → `code-reviewer`                         | Iterate on fixes until merge-ready                         |
| **Incident Follow-up**       | Post-incident learnings           | `incident-scribe` → `story-builder`                                                | Convert incident findings into future stories/improvements |

### Key Iteration Patterns

#### **TDD Loop (Tight Integration: Stages 4-5)**

The tightest loop is between **Implementation** and **Testing**, following
**Red→Green→Refactor**:

```
Red Phase (test-drafter):
  └─> Write failing test based on acceptance criteria

Green Phase (implementation-driver):
  └─> Write minimal code to pass the test

Refactor Phase (implementation-driver):
  └─> Improve code structure while keeping tests green

Validation (test-truth-and-stability-gate):
  └─> Verify test quality, determinism, and coverage
```

#### **Quality Gate Loops (Stages 1-3)**

Stories and architecture are refined before implementation begins, reducing
costly rework:

```
Requirements Stage:
  └─> story-builder creates story
  └─> story-quality-gate validates INVEST & DoR
  └─> If gaps found: ─> story-builder refines

Architecture Stage:
  └─> arch-spec-author creates design
  └─> risk-and-nfr-gate reviews security/NFRs
  └─> If issues found: ─> arch-spec-author refines
```

#### **Review Loop (Stage 6)**

Code review feedback drives refinement before merge:

```
code-reviewer comments on PR
  └─> review-comment-fixer implements changes
  └─> code-reviewer validates fixes
  └─> merge-readiness-auditor approves for merge
```

______________________________________________________________________

## 🤖 Custom Copilot Agents

This template includes pre-defined custom GitHub Copilot agents for each
lifecycle stage. These agents are specialized with domain knowledge and
guardrails:

- **Builder Agents** (create artifacts): `requirements`, `story-builder`,
  `ui-scaffolder`, `arch-spec-author`, `implementation-driver`, `test-drafter`,
  etc.
- **Gate Agents** (quality control): `story-quality-gate`, `a11y-guardian`,
  `risk-and-nfr-gate`, `code-reviewer`, `merge-readiness-auditor`, etc.

See
[Agent Workflow Diagram](docs/best_practices/web-dev-lifecycle/agent-workflow-diagram.md)
for the complete agent inventory and orchestration.

______________________________________________________________________

## 📁 Repository Structure

```
├── .github/
│   ├── agents/              # Custom GitHub Copilot agent definitions
│   ├── ISSUE_TEMPLATE/      # Structured issue templates (01-feature, 02-story, etc.)
│   ├── skills/              # Reusable agent skill definitions
│   └── copilot-instructions.md  # Universal Copilot rules (INVEST, DoR, output format)
├── docs/
│   └── best_practices/
│       └── web-dev-lifecycle/  # 8-stage lifecycle guides with Copilot integration
├── src/
│   ├── backend/             # Backend code template
│   └── frontend/            # Frontend code template
└── scripts/                 # Build and automation scripts
```

______________________________________________________________________

## 🎯 Key Principles

### 1. **INVEST User Stories**

All user stories must be **Independent**, **Negotiable**, **Valuable**,
**Estimable**, **Small**, and **Testable**.

### 2. **Definition of Ready (DoR)**

Stories are not ready for implementation until:

- ✅ User value is clearly stated
- ✅ Success metrics are defined
- ✅ Acceptance criteria are complete (happy path + edge cases)
- ✅ Dependencies are identified
- ✅ Out of scope is explicit
- ✅ Data model impact is assessed
- ✅ Security/privacy implications are reviewed
- ✅ UX states are defined (loading, empty, error)

### 3. **Test-Driven Development (TDD)**

Implementation follows **Red→Green→Refactor**:

- **Red**: Write failing tests first
- **Green**: Write minimal code to pass tests
- **Refactor**: Improve code structure while maintaining test green status

### 4. **Quality Gates**

Each stage has automated quality gates:

- Story validation (INVEST, testability)
- Accessibility audits (WCAG compliance)
- Architecture reviews (security, NFRs)
- CI quality checks (lint, tests, coverage)
- Code reviews (correctness, maintainability)
- Merge readiness audits

______________________________________________________________________

## 📚 Documentation

- [Web Development Lifecycle Guides](docs/best_practices/web-dev-lifecycle/) —
  Stage-by-stage integration with Copilot
- [GitHub Copilot Best Practices](docs/best_practices/copilot-custom-agents-best-practices.md)
  — Agent design and prompting
- [User Stories Best Practices](docs/best_practices/web-dev-lifecycle/03-user-stories-copilot-integration.md)
  — INVEST principles and acceptance criteria
- [TDD Best Practices](docs/best_practices/tdd-best-practices.md) — Test-driven
  development workflows
- [Git Commit Message Best Practices](docs/best_practices/git-commit-message-best-practices.md)
  — Clear, traceable commit messages

______________________________________________________________________

## ⚡ Quick Start (Template Usage)

### 1) Create from Template

- GitHub UI: Click “Use this template” on this repository.
- CLI (optional):

```bash
# Requires GitHub CLI (gh) and authentication
gh repo create <your-repo-name> --template grammy-jiang/agentic-dev-template --public
git clone https://github.com/<your-org>/<your-repo-name>.git
cd <your-repo-name>
```

### 2) Open in VS Code and Enable Copilot

- Install the GitHub Copilot extension and sign in.
- Open the workspace and ensure extensions can read
  `.github/copilot-instructions.md`.

### 3) Minimal Usage Example

Use Copilot Chat to draft a story and create an issue in your repo:

```text
/story-builder
Feature: Allow users to export data as CSV
Success metrics: 95% task completion in usability test
Constraints: Must support >100k rows, maintain memory safety
Acceptance criteria: Given/When/Then for happy path + errors
Out of scope: XLSX formatting, pivot tables
```

Then create an issue with the `02-user-story.yml` template and iterate using the
quality gates.

______________________________________________________________________

## 🧭 Documentation Funnel

- **Lifecycle guides:** See `docs/best_practices/web-dev-lifecycle/` for
  stage-by-stage usage.
- **Architecture & design:** See `docs/best_practices/` for ADRs, diagrams, and
  specs.
- **Contribution & development:** See `CONTRIBUTING.md` for dev setup and
  workflows.

Keep README focused on onboarding; deeper material lives in `docs/`.

______________________________________________________________________

## 🙋 Support

- For your project derived from this template: open issues in your repository
  and use the provided issue forms.
- For template improvements or bugs: open an issue in this template repository.

______________________________________________________________________

## 🤝 Contributing

Contributions to improve the template are welcome. See `CONTRIBUTING.md` for
guidelines and development setup.

______________________________________________________________________

## 📄 License

This repository is a template. Choose and add a `LICENSE` file in your derived
project (e.g., MIT/Apache-2.0). If contributing here, changes are provided under
the repository’s chosen license once added.

______________________________________________________________________

## 🔗 Related Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [INVEST User Story Principles](<https://en.wikipedia.org/wiki/INVEST_(mnemonic)>)
- [Agile Acceptance Criteria (BDD/Gherkin)](https://cucumber.io/docs/gherkin/)
- [Architecture Decision Records (ADRs)](https://adr.github.io/)
- [CI/CD Best Practices](https://martinfowler.com/articles/continuousIntegration.html)
