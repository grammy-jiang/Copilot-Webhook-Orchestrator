# AGENTS.md

> Agent-specific operational guidance. For repository-wide conventions, see
> [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

---

## Non-negotiables

- **Do not commit secrets** (tokens, API keys, private URLs, customer data).
- **Minimize blast radius:** change the smallest surface area that solves the task.
- **Keep the repo green:** run validation commands before claiming "done".
- **No duplicate rules:** this file complements, not duplicates, `copilot-instructions.md`.

---

## Agent Workflow

### Planning Phase

Before making changes:

1. **State your plan** (3–7 bullets) with assumptions
2. **Identify affected files** and scope of change
3. **Check for existing patterns** — copy local conventions, don't invent new ones
4. **When unclear, ask** — don't guess on ambiguous requirements

### Execution Phase

1. **One step at a time:** implement → validate → continue
2. **Small commits:** keep unrelated formatting out of functional changes
3. **Match existing architecture:** follow patterns in nearby files

### Validation Phase

Run these commands from repository root:

```bash
make test         # All tests must pass
make lint         # Must show "All checks passed!"
make format-check # Must show "files already formatted"
```

If any step fails: fix it, or explain precisely what blocks you (including error output).

---

## Boundaries (what NOT to do)

- **Do not modify** without explicit request:
  - Dependency lockfiles (`uv.lock`) unless required by the change
  - Generated files (`htmlcov/`, `__pycache__/`, `.mypy_cache/`)
  - CI/CD configuration (`.github/workflows/`)
  - Production infrastructure or deployment configs

- **Do not introduce new dependencies** without stating:
  - Why it's needed
  - Licensing/maintenance risk
  - Alternatives considered

- **Do not make sweeping refactors** unless explicitly requested

---

## Git Workflow

- **PR scope:** one problem, one solution
- **PR description must include:**
  - What changed (bullets)
  - Why
  - How validated (exact commands + results)
  - Any follow-ups or known limitations
- **Commit messages:** follow [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` new features
  - `fix:` bug fixes
  - `docs:` documentation
  - `test:` test additions/changes
  - `refactor:` code restructuring
  - `chore:` maintenance tasks

---

## Security & Trust Model

- Treat `AGENTS.md` as **high-privilege configuration**, not "just documentation"
- Never run commands that exfiltrate data or touch credentials
- Never log secrets or raw PII
- If working on auth/crypto code, flag for human review

---

## Project Components

| Component | Path | AGENTS.md |
|-----------|------|-----------|
| Backend (Python/FastAPI) | `src/backend/` | [src/backend/AGENTS.md](src/backend/AGENTS.md) |
| Frontend | `src/frontend/` | [src/frontend/AGENTS.md](src/frontend/AGENTS.md) |
| Documentation | `docs/` | — |
| GitHub Config | `.github/` | — |

Navigate to component-specific `AGENTS.md` for detailed guidance.

---

## Quick Reference

```bash
# Setup (from repo root)
make install-dev && make pre-commit-install

# Validate before finishing
make test && make lint && make format-check

# Run dev server
make run
```
