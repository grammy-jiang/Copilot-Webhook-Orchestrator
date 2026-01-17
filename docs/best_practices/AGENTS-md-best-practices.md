# AGENTS.md Best Practices for Full-Stack Copilot Use

**Placement and Scope**: Create a single `AGENTS.md` at your repo root (GitHub
Copilot will even scaffold one). Copilot (VS Code extension, CLI, and Coding
Agent) automatically reads this file and includes its content in prompt context.
You can also add nested `AGENTS.md` in subfolders for large or multi-module
projects – Copilot always uses the nearest file in the directory tree. (By
default VS Code may ignore files outside the workspace root unless you enable
that setting.) In short, **one `AGENTS.md` works for all Copilot agents**.

**Key Sections and Content**: Structure `AGENTS.md` with clear Markdown headings
and bullet lists. Common sections include: *Project Overview* or architecture
notes; *Setup/Dev Environment* commands; *Build & Run* commands; *Testing*
instructions; *Code Style* guidelines; *CI/Deployment* notes; *Security
Considerations*; and *Contributing/PR* rules. For example, include steps like
"Install deps: `pip install -r requirements.txt`", lint/test commands, or
database migration commands. You can literally copy the pattern from the
official AGENTS.md site example – it uses `##` headings and `-` lists to group
tips (see **"Dev environment tips"**, **"Testing instructions"**, etc.).

- **Environment & Setup**: Describe language/runtime versions, dependencies, and
  how to start dev servers. E.g. for Python: "Activate the virtualenv
  (`python -m venv venv`), install requirements
  (`pip install -r requirements.txt`), then run `flask run` or
  `uvicorn main:app --reload`." For JS/TS: "Use Node LTS, run `npm ci` or
  `pnpm install`, then `npm start` or `npm run dev`."

- **Build/Test Commands**: List commands for building and testing each part:
  e.g. "Backend tests: `pytest tests/`; Frontend tests: `npm test`." Include any
  CI commands or workflow pointers (like mentioning `.github/workflows`).

- **Code Style/Conventions**: Spell out linters/formatters. For Python, "PEP 8
  with Black and isort (line length 88) and type hints" (see e.g. Wegent
  AGENTS.md) and testing styles. For TS/JS, mention ESLint/Prettier or project
  conventions. You can show short code examples or good-vs-bad snippets in
  fenced code blocks to clarify style.

- **Workflow & Git**: Outline commit/PR rules, branch naming, or review checks.
  For instance: "Run lint and tests before committing; PR titles should follow
  `[module] Short summary`. Always tag reviewer."

**Task Prompts and Agent Guidance**: You can include a section (e.g. "## Tasks"
or "## Agents") that briefly describes common tasks or roles. Use plain-English
bullet lists to define tasks or questions the AI might handle (e.g. "- Implement
new API endpoint: ensure it follows REST conventions"). Phrase instructions in
the imperative and be explicit. It’s helpful to use clear "Always do…" or "Never
do…" rules (for example, "Always run all tests and code analysis before
merging," “Never commit secrets"). These boundary rules guide the agent’s
behavior. If using Copilot CLI with custom tools, you can even reference tools
by name (e.g. using `#tool:grep`) in AGENTS.md to tailor how it searches files.

**Examples – Python Backend**: A Python section might look like:

```markdown
## Backend (Python)
- **Environment:** Python 3.10+ (use a virtualenv or conda).
- **Dependencies:** Run `pip install -r requirements.txt`.
- **Run:** Start the server with `flask run` or `uvicorn main:app --reload`.
- **Testing:** Use `pytest tests/` (all tests must pass).
- **Style:** Follow PEP 8. Run `black .` and `isort .` to format code. Use type hints and docstrings.
- **Database:** Run migrations: `alembic upgrade head`. Seed dev data with `python seed_db.py`.
```

**Examples – JS/TS Frontend**: A JavaScript/TypeScript section could be:

```markdown
## Frontend (JavaScript/TypeScript)
- **Environment:** Node.js 18 LTS, use `npm ci` or `pnpm install`.
- **Dev Server:** Run `npm start` (for React) or `npm run dev` (for Next.js).
- **Build:** Use `npm run build` for production bundle.
- **Testing:** Run `npm test` (Jest/Vitest) and ensure all tests pass.
- **Style:** Follow ESLint/Prettier rules. For example, run `npm run lint` and `npm run format` before commits.
- **Deploy:** Docs or commands for deploying the frontend (e.g. `npm run export` for static sites).
```

**Maintaining the File**: Keep `AGENTS.md` up-to-date with the project. Treat it
like part of your docs: update it whenever you add new services, change build
commands, or tighten code standards. Be *explicit and concise* – agents work
better with clear rules and examples. Link to detailed docs or README for
lengthy info. As the project evolves, version control will track changes in
`AGENTS.md`, so review it on each major refactor or dependency bump. In a
monorepo or multi-component repo, continue using nested `AGENTS.md` files so
each part has its own guide.

**Copilot-Specific Tips**: Remember that Copilot automatically prepends your
prompts with the markdown in `AGENTS.md`. Use this to your advantage:
well-structured markdown helps it parse context. Embed code snippets, examples,
or sample inputs in fenced code blocks – the models pay attention to those cues.
Write instructions the way you’d ask a teammate: bullet lists and short steps
work well. For instance, GitHub’s guide shows using `-` list items under
headings to clearly separate tips.

Finally, use Copilot’s custom instructions features: in VS Code or CLI, ensure
custom instructions are enabled. (By default, VS Code may ignore nested files
unless toggled on.) If using the CLI, note it already recognizes `AGENTS.md` for
repository context. You can also experiment with Copilot’s new features like
**Agent Skills** and **GitHub Copilot Coding Agent**, which now natively read
`AGENTS.md`. In short, treat `AGENTS.md` as a “source of truth” for your
project’s coding conventions – clear, up-to-date markdown there will measurably
improve Copilot’s code suggestions and multi-step task support.

**Sources**: GitHub Copilot documentation and community resources on AGENTS.md
usage
