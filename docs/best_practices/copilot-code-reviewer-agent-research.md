# Creating a Custom GitHub Copilot Code Reviewer Agent

GitHub Copilot’s recent support for **custom agents** and **instructions**
allows developers to tailor AI-assisted code reviews to their specific standards
and workflows. This report covers how to create a custom Copilot agent for code
review, analyzes the structure of a `code-reviewer.agent.md` prompt, and
provides guidance on crafting effective review prompts (with a focus on Python
backend and JavaScript/TypeScript frontend code). It also surveys tools and
extensions that support custom Copilot agents.

______________________________________________________________________

## Best Practices for Custom Code Review Agents

When designing a custom Copilot code review agent, these practices consistently
improve output quality and predictability:

### 1) Use YAML frontmatter (agent metadata)

Start the `.agent.md` file with YAML metadata to define the agent’s name,
description, model, and tool permissions. Typical fields include:

- `name`, `description`
- `model`
- `tools` (what the agent may access/do)
- `infer` (whether Copilot can auto-select the agent)
- optional `metadata` (team/category tags)

### 2) Define role and scope explicitly

State the agent’s job in the first lines (e.g., “expert code reviewer focusing
on security, quality, performance”). This anchors behavior and reduces generic
responses.

### 3) Write like a checklist (structured headings + bullets)

Copilot follows structured prompts well. Recommended sections:

- **Review dimensions** (Security / Code Quality / Performance / Testing)
- **Severity levels** (Critical / Important / Suggestions)
- **Output format** (tables, sections, summary)
- **Principles** (be specific, cite file+line, suggest fixes)
- **Escalation criteria** (when to flag humans)

### 4) Be concise and specific

Prefer short, imperative bullets over long paragraphs. Avoid conflicting rules.

### 5) Include examples

Show:

- a sample output report (tables + severity)
- “good vs bad” short snippets for style rules
- examples of actionable feedback (why it matters + how to fix)

### 6) Iterate based on real reviews

Treat the prompt as a living spec. Run it on PRs, adjust:

- noise reduction (confidence thresholds)
- what to ignore (formatting handled by linters)
- what to prioritize (security, correctness)

### 7) Keep prompt size manageable

Very long prompts dilute instructions. Keep it focused; split into separate
instruction files where possible.

______________________________________________________________________

## Inside `code-reviewer.agent.md`: Structure and Behavioral Impact

A typical `code-reviewer.agent.md` is effectively an SOP for the AI.

### A) YAML metadata

Example (illustrative):

```yaml
---
name: "Code Reviewer"
description: "Comprehensive code review specialist focusing on security, quality, performance, and best practices."
tools: ["read", "search", "github/*"]
model: "GPT-4"
infer: true
metadata:
  team: "engineering"
  category: "quality-assurance"
---
```

**Impact:** controls discoverability, permissions, and selection behavior.

### B) Role definition

A single paragraph describing the agent as an “expert reviewer” with focus
areas.

**Impact:** sets tone and priorities; reduces “assistant-like” generic replies.

### C) Review framework / dimensions

Checklist-style sections:

- **Security**: OWASP-style checks, secrets, authz/authn, input validation.
- **Code Quality**: naming, SRP, DRY, error handling.
- **Performance**: query patterns, complexity, caching.
- **Testing**: presence and quality of tests, edge cases, reliability.

**Impact:** makes coverage systematic and repeatable.

### D) Output format template

A Markdown template for:

- Critical Issues (blocks merge)
- Important Issues (needs discussion)
- Suggestions (non-blocking)
- Positive highlights
- Review summary + recommendation

**Impact:** enforces consistent reporting and actionable structure.

### E) Review principles and escalation criteria

Rules like:

- cite file and line
- explain *why* it’s an issue
- suggest concrete fixes
- flag high-risk issues to humans

**Impact:** improves signal-to-noise and safety.

______________________________________________________________________

## Crafting Effective Reviewer Prompts for Python and JS/TS

### Python backend (practical review focus)

#### Security

- Parameterized DB access; avoid string-built SQL
- No hardcoded secrets; avoid logging sensitive data
- Validate/sanitize external input
- Avoid unsafe dynamic execution (`eval`, `exec`) on untrusted data
- Ensure authorization checks for protected endpoints

#### Readability & style

- Enforce PEP 8 conventions (or project standards like Black)
- Clear naming, small functions, avoid deep nesting
- Avoid classic pitfalls (e.g., mutable default arguments)
- Require type hints for public APIs if that’s your standard

#### Maintainability & design

- SRP, modular boundaries (routes/controllers vs business logic)
- Robust error handling (avoid blanket `except Exception` unless justified)
- Use context managers for resources (files, connections)
- Require tests for critical paths (unit + smoke + e2e as appropriate)

#### Framework-specific guidance (optional)

Add rules per framework (Django/FastAPI/Flask):

- input validation patterns
- auth middleware checks
- migration presence when models change
- ORM query anti-patterns (N+1, unbounded `.all()` etc.)

______________________________________________________________________

### JavaScript/TypeScript frontend (practical review focus)

#### Security

- XSS risks: avoid unsafe HTML injection
- No secrets in client code
- Safe token handling (avoid risky storage patterns)
- Validate/sanitize user-driven data before DOM use

#### Code quality & readability

- Prefer `const` when not reassigning
- Avoid `any` in TypeScript; define types/interfaces
- Prefer `async/await` for readable async flows
- Avoid overly complex promise chains and nested callbacks

#### Maintainability & performance

- Avoid unnecessary re-renders (React) and expensive computations in render
- Avoid direct state mutation; follow framework idioms
- Keep components reasonably sized; refactor reusable logic
- Add tests for key behaviors (unit + component tests; e2e for workflows)

#### Style compliance

- Align with ESLint/Prettier rules
- Prefer the AI to focus on *logical* issues; let formatters handle formatting

______________________________________________________________________

## Tooling and Ecosystem Options

### 1) Copilot PR Code Review + custom instructions

For GitHub PR reviews, you can tune Copilot’s reviewer using repository-level
instruction files (and path-specific instruction files). This is often more
maintainable than a single giant prompt.

### 2) Custom agents in VS Code and Copilot CLI

Create `.agent.md` files for specialized sessions (reviewer vs fixer vs
security). Use them as separate “modes” to reduce context pollution.

### 3) Copilot Labs (optional)

Useful for interactive transformations, explanations, and test generation. Not a
full agent system, but complements review workflows.

### 4) LangChain / advanced orchestration (optional)

If you want a pipeline that fetches diffs, runs analysis, and posts a formatted
report, orchestration frameworks can help. This is more engineering effort and
depends on access to underlying model APIs.

### 5) Community prompt libraries

- Collections of “reviewer prompts” can serve as templates (security reviewer,
  performance reviewer, framework-specific reviewer).
- Use them to bootstrap your agent structure and adapt to your standards.

______________________________________________________________________

## Practical Next Steps (Recommended)

1. **Start with a single `code-reviewer.agent.md`** using:
   - role + review dimensions + severity
   - strict output format
   - explicit “only comment when confident” rule
1. **Split rules by language** into `*.instructions.md` files if you want
   tighter targeting:
   - `python.instructions.md` -> `applyTo: "**/*.py"`
   - `frontend.instructions.md` -> `applyTo: "**/*.{js,jsx,ts,tsx}"`
1. **Pair with linters/formatters** so the AI focuses on correctness and design
   (not whitespace).
1. **Run on 5–10 real PRs**, tune:
   - reduce noise
   - add org-specific gotchas
   - refine severity thresholds

______________________________________________________________________

## Reference Notes (Non-exhaustive)

This report was synthesized from GitHub Copilot prompt/agent conventions,
community agent templates, and practitioner writeups about tuning Copilot’s code
review behavior via instructions.
