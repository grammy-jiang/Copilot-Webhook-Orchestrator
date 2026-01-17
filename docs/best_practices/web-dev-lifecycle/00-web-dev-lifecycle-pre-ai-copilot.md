# Traditional Website Development Lifecycle (pre‑2022) and How to Fit GitHub Copilot Into It

______________________________________________________________________

### 1. Feature Requirements Gathering

Before the AI era, requirements gathering typically followed either
**Waterfall** or **Agile** models.

- **Waterfall:** requirements were defined up front in PRDs/BRDs; change control
  was formal and costly.
- **Agile (Scrum/Kanban):** requirements evolved; work was expressed as **epics
  → user stories → tasks** and refined continuously.

**Pre‑2022 best practices**

- **Stakeholder collaboration:** workshops, interviews, surveys, domain expert
  reviews.
- **Prioritisation:** MoSCoW, RICE, WSJF; clarify business value vs. complexity
  vs. risk.
- **Definition of Done/Ready:** explicit quality bar and entry criteria for
  engineering.
- **Traceability:** link business goals → epics → stories → acceptance criteria
  → tests.

**How Copilot fits**

- Draft story candidates, acceptance criteria, and edge cases from raw notes (VS
  Code Copilot Chat / Copilot CLI).
- Produce structured PRD/user‑story templates; standardise phrasing; generate
  “out of scope” lists.
- Turn meeting notes into backlog items (human reviews and final accountability
  still required).

______________________________________________________________________

### 2. UI/UX Design

UX work was driven by **user‑centred design** and design thinking: empathise →
define → ideate → prototype → test → iterate.

**Pre‑2022 best practices**

- Personas, journeys, task flows.
- Wireframes → interactive prototypes (Figma/Sketch/XD).
- Accessibility (WCAG), responsive design, consistent design systems.
- Usability testing and iterative refinement.

**How Copilot fits**

- Translate UI specs into component scaffolds and boilerplate (React/Vue/etc.)
  in VS Code.
- Generate realistic mock data and fixtures quickly (CLI/Chat).
- Summarise design feedback into actionable tickets (Chat/CLI).

______________________________________________________________________

### 3. User Stories

User stories were the unit of delivery in Agile environments:

> **As a** [persona], **I want** [capability], **so that** [benefit].

**Pre‑2022 best practices**

- Apply **INVEST** (Independent, Negotiable, Valuable, Estimable, Small,
  Testable).
- “3 C’s”: Card, Conversation, Confirmation.
- Clear **acceptance criteria** (often Given/When/Then).
- Break epics into small, verifiable slices.

**How Copilot fits**

- Generate candidate stories + Given/When/Then criteria from a feature brief.
- Propose negative/edge‑case acceptance tests (rate limiting, permission errors,
  empty states).
- Enforce consistent formatting and checklists across issues.

______________________________________________________________________

### 4. Implementation Specifications & Architecture

Teams produced design docs and technical specs to reduce ambiguity.

**Pre‑2022 best practices**

- Architecture docs (C4/UML), API contracts (OpenAPI), data models, ADRs.
- Non‑functional requirements: security, performance, reliability,
  observability.
- Spikes/proofs‑of‑concept for risk reduction.
- Living documentation: updated alongside code.

**How Copilot fits**

- Generate Mermaid/PlantUML diagrams from written flows.
- Draft OpenAPI schemas and validate completeness.
- Create initial skeletons: service layout, typed DTOs, repository/service
  layers, migrations.
- Act as a “second reviewer” for consistency gaps in docs.

______________________________________________________________________

### 5. Coding Practices & Development Workflows

Pre‑2022 maturity looked like “CI‑first, review‑first”.

**Pre‑2022 best practices**

- Git workflows: feature branches, PRs, CI gates; trend toward trunk‑based
  development.
- Style enforcement: formatters, linters, static analysis.
- Small PRs, meaningful commits, clear change logs.
- Secure coding standards; secrets management; dependency hygiene.

**How Copilot fits**

- Accelerate routine coding while enforcing project conventions (your repo
  prompts, templates, lint rules).
- Refactor repetitious code safely with guided prompts + tests.
- Use Copilot CLI for quick scripts, migrations, refactors, and “explain this
  code” tasks.

______________________________________________________________________

### 6. Testing (Unit/Integration/E2E)

Testing was layered, with automation increasingly embedded into CI.

**Pre‑2022 best practices**

- Unit tests for business logic; integration tests for module boundaries.
- E2E/UI tests (Selenium/Cypress/Playwright) for critical user journeys.
- Shift‑left testing and regression suites in CI.
- Test data management and deterministic environments.

**How Copilot fits**

- Generate unit tests and fixtures for existing code (then hard‑review for
  correctness).
- Suggest missing scenarios (timeouts, retries, auth failures, malformed
  payloads).
- Draft E2E flows quickly (Playwright/Cypress) and turn them into stable CI
  tests.

______________________________________________________________________

### 7. Code Review & Quality Assurance

Peer review remained the primary quality lever.

**Pre‑2022 best practices**

- PR templates/checklists; “two‑eyes” principle; reviewers focus on correctness,
  security, maintainability.
- Automated checks: lint, tests, SAST, dependency scanning.
- QA/UAT on staging environments; release notes and regression criteria.

**How Copilot fits**

- Copilot Chat as a “pre‑review” to catch obvious issues before human review.
- Summarise diffs, highlight risks, propose refactors with rationale.
- With Coding Agent: handle small fixes and create PRs for review (humans still
  gate merges).

______________________________________________________________________

### 8. Deployment & Maintenance

By 2021, CI/CD and DevOps practices were common.

**Pre‑2022 best practices**

- Multi‑stage environments: dev → test → staging → prod.
- Deployment strategies: blue‑green, canary, feature flags.
- Observability: logs, metrics, traces; alerts and incident runbooks.
- Maintenance: dependency updates, security patches, performance tuning,
  post‑mortems.

**How Copilot fits**

- Generate CI pipelines (GitHub Actions), Dockerfiles, Helm/K8s manifests,
  runbooks.
- Automate “ops PRs” (small changes) via Coding Agent.
- Draft incident summaries and RCA templates from timelines (human validation
  required).

______________________________________________________________________

## A Practical “AI‑Assisted” Lifecycle (recommended operating model)

You can keep the traditional lifecycle, but add Copilot touchpoints:

1. **Requirements →** Copilot drafts stories/criteria; you approve.
1. **Design →** Copilot scaffolds UI code; you validate UX and accessibility.
1. **Spec/Architecture →** Copilot generates diagrams/contracts; you decide
   tradeoffs.
1. **Implementation →** Copilot speeds coding; CI + lint + tests enforce
   quality.
1. **Testing →** Copilot drafts tests; you curate and stabilise.
1. **Review →** Copilot pre‑review + humans gate merge.
1. **Release →** Copilot generates pipelines/docs; you own production risk.

______________________________________________________________________

## References (high-level, non-exhaustive)

- Agile/Scrum & user stories (INVEST, acceptance criteria, BDD/Gherkin).
- Design thinking / user-centred design processes.
- C4/UML architecture documentation, ADR patterns, OpenAPI.
- CI/CD, trunk-based development, PR-based code review best practices.
- Testing pyramids and shift-left testing principles.
