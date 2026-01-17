# UI/UX Design Stage: Integrating GitHub Copilot to Generate UI Skeleton + Mock Data (You Gate UX/A11y)

If you want custom agents to reliably produce **front-end scaffolds that match
your UX intent** (and don’t quietly degrade accessibility), you need: **(1) a
design-to-code contract**, **(2) strict repo instructions**, and **(3) prompt
playbooks**.

______________________________________________________________________

## A. Baseline setup (so Copilot doesn’t freestyle your UI)

### 1) Repo instructions = “policy + guardrails”

Use both, because they target different surfaces:

- **VS Code Copilot custom instructions**: `.github/copilot-instructions.md`
  (workspace-wide behavior).
- **Path-specific instructions**: `.github/instructions/*.instructions.md` with
  `applyTo` to enforce rules for UI code vs docs vs tests.
- **Agent roster / boundaries**: `AGENTS.md` (your internal governance doc: what
  each agent is allowed to do, and what it must never do).

Concrete “policy” items to encode:

- **Design-system first**: use existing components/tokens before introducing new
  UI patterns.
- **A11y baseline**: semantic HTML, keyboard navigation, focus management; ARIA
  only when needed; never ship inaccessible defaults.
- **State completeness**: loading/empty/error/permission-denied states are
  mandatory.
- **No new deps by default**: adding UI libraries needs explicit approval
  (prevents dependency sprawl).

### 2) Prompt files = “standard operating procedures”

Put reusable prompts in `.github/prompts/*.prompt.md` so you can run them
consistently in chat.

### 3) Grounding = “work from the real codebase”

Use `@workspace` so Copilot understands your current component architecture,
routing, styling, and patterns (instead of inventing a new framework inside your
repo).

______________________________________________________________________

## B. UI/UX-to-code workflow with Copilot embedded (end-to-end)

### 1) Design intake → “UI contract”

**Goal:** turn design artifacts into a code-ready brief.

**Inputs you provide:**

- target route(s), user goal, interactions
- required components + variants
- responsive requirements
- copy/text + empty/error messages
- a11y expectations (keyboard flow, focus order, ARIA expectations)

**Copilot outputs (drafts):**

- a **UI contract** (structured spec) + open questions list
- a component inventory: what exists vs what must be created

**Gate:** if responsive + states + a11y aren’t specified, it’s not
“design-ready.”

______________________________________________________________________

### 2) Component mapping → “reuse vs build”

**Goal:** prevent parallel component systems.

**Copilot does:**

- discovers existing components/design tokens (via `@workspace`)
- proposes reuse plan + minimal new components

**Gate:** any new component must justify why an existing one cannot be extended.

______________________________________________________________________

### 3) UI skeleton generation → “scaffold + stories”

**Goal:** generate maintainable scaffolding, not finished UI art.

**Copilot does:**

- scaffolds React/TS components, routing, layout structure
- creates **Storybook stories** (or equivalent) per state/variant
- adds placeholder styling hooks tied to tokens (not hard-coded magic numbers)

**Gate:** PR must include loading/empty/error states by default.

______________________________________________________________________

### 4) Mock data + fixtures → “realistic, typed, repeatable”

**Goal:** unblock UI development without backend coupling.

**Copilot does:**

- generates **typed mock models** (TS types aligned to API contracts)
- creates fixtures for: happy path + edge cases
- optionally generates MSW handlers / mock endpoints

**Gate:** mocks must be deterministic and cover negative states (permission
denied, validation error, network error, empty list).

______________________________________________________________________

### 5) A11y enforcement → “audit + fixes”

**Goal:** ship accessible-by-default components.

**Copilot does:**

- runs a checklist pass and proposes code-level fixes:
  - semantic structure (headings, landmarks)
  - keyboard interactions (tab order, ESC to close, etc.)
  - focus management (modals/drawers)
  - ARIA labeling and live regions (only where appropriate)

**Gate:** anything interactive must be keyboard-usable and have visible focus
states.

______________________________________________________________________

### 6) Handoff evidence → “prove it works”

**Goal:** reduce review friction and rework.

**Copilot does:**

- generates a “verification evidence” section:
  - Storybook links / screenshots
  - key flows exercised
  - a11y checklist outcome
  - test notes

**Gate:** reviewers shouldn’t need to guess what was validated.

______________________________________________________________________

### 7) Live browser verification → "real UX validation with MCP"

**Goal:** verify UI behavior and backend integration in a real browser.

Use **browser MCP tools** (Playwright, Chrome, Firefox) to validate:

**UX Behavior Verification:**

- navigation flows work as designed
- interactive elements respond correctly (buttons, forms, modals)
- state transitions render properly (loading → success → error)
- responsive layouts adapt at breakpoints
- animations and visual feedback behave as expected

**Frontend-Backend Communication:**

- API calls are made correctly (verify in Network panel)
- API responses render correctly in the UI
- error states display appropriate user feedback
- loading indicators appear during async operations
- authentication flows work (login, logout, protected routes)

**Verification workflow:**

```typescript
// 1. Navigate and verify UX
await page.goto('/dashboard');
await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

// 2. Verify API integration
const [request] = await Promise.all([
  page.waitForRequest('/api/users'),
  page.getByRole('button', { name: 'Load Users' }).click(),
]);
await expect(page.getByTestId('user-list')).toBeVisible();

// 3. Verify error handling
await page.route('/api/data', route => route.fulfill({ status: 500 }));
await page.reload();
await expect(page.getByTestId('error-state')).toBeVisible();
```

**Gate:** critical user flows must be verified in a real browser before PR.

______________________________________________________________________

## C. Where Copilot CLI / Coding Agent fits

- Use **Copilot CLI** to delegate scaffolding work to the coding agent and get a
  draft PR back (excellent for repetitive UI skeleton + fixture creation).
- Define **custom agents** (frontmatter + prompt body) to standardize behavior
  across VS Code / CLI / coding agent.
- Keep governance strict: the agent produces PRs; humans approve merges.

______________________________________________________________________

## D. Recommended custom agents for this stage (keep it pragmatic)

If you prefer “agent for the big step + prompt files for repeatable tasks”, this
structure is high ROI:

### 1) `ui-scaffolder.agent.md` (primary agent)

**Mission:** generate UI skeletons that match the UI contract, reuse existing
components, and include all states.

**Non-negotiables:**

- reuse design system first
- create states (loading/empty/error/permission-denied)
- no new dependencies unless asked
- produce Storybook stories (or documented demo pages)

### 2) `a11y-guardian.agent.md` (quality gate agent)

**Mission:** treat accessibility as a release blocker; propose concrete fixes.

**Non-negotiables:**

- keyboard usable interactions
- focus management for overlays
- semantic HTML before ARIA

### Optional skills (useful, not mandatory)

- `mock-data-factory` — fixtures + MSW handlers + edge cases
- `storybook-writer` — story variants for states
- `a11y-checklist` — a11y audit checklist + required evidence

______________________________________________________________________

## E. Prompt file “command set” (what you actually run day-to-day)

Store these under `.github/prompts/`:

- `/ui-intake-contract` → produce UI contract + open questions
- `/ui-scaffold-from-contract` → scaffold components + routing + layout
- `/mock-data-fixtures` → types + fixtures + MSW handlers
- `/a11y-audit-and-fix-plan` → checklist + code fix plan
- `/storybook-states` → stories for loading/empty/error variants
- `/handoff-evidence` → verification evidence template

______________________________________________________________________

## Example prompt file skeleton (UI scaffolding)

```markdown
---
name: ui-scaffold-from-contract
description: Scaffold UI components + states + stories from a UI contract
agent: ui-scaffolder
tools: [workspace]
---

Input: ${input:ui_contract:Paste the UI contract}

Rules:
- Reuse existing components from this repo via @workspace discovery.
- Generate loading/empty/error/permission-denied states by default.
- No new dependencies unless explicitly requested.
- Produce Storybook stories (or demo page) for each state.

Deliverables:
1) Component scaffolds (React/TS)
2) Mock data hooks/interfaces (typed)
3) Stories/demos for each state
4) Open questions and assumptions (explicit)
```

______________________________________________________________________

## Next step suggestion

If you want to proceed one-by-one, the next concrete deliverable is to produce:

- `.github/agents/ui-scaffolder.agent.md`
- `.github/agents/a11y-guardian.agent.md`
- Six `.github/prompts/*.prompt.md` files corresponding to the command set above
- A minimal policy layer in `.github/copilot-instructions.md` + path-specific
  `.github/instructions/*.instructions.md`
