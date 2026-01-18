# ADR-005: Frontend Stack Selection

**Status:** Accepted

**Date:** January 18, 2026

**Deciders:** @ui-scaffolder, @arch-spec-author

______________________________________________________________________

## Context

Phase 1 of the Copilot Workflow Orchestrator requires a frontend for:

- User authentication (GitHub OAuth login/logout)
- Repository management (list, search, health status)
- Event stream viewing (timeline, filters, pagination)
- Dashboard (repository grid, active issues/PRs, queue depth)

The architecture brief specifies SvelteKit with Tailwind CSS. This ADR
documents the specific technology choices for the frontend implementation.

______________________________________________________________________

## Decision

We will use the following frontend stack:

| Category             | Choice                           | Version    |
| -------------------- | -------------------------------- | ---------- |
| Framework            | SvelteKit                        | 2.x        |
| Language             | Svelte                           | 5.x        |
| Package Manager      | pnpm                             | 9.x        |
| CSS Framework        | Tailwind CSS                     | 3.x        |
| UI Components        | shadcn-svelte                    | latest     |
| Unit/Component Tests | Vitest + @testing-library/svelte | 2.x / 5.x  |
| E2E Tests            | Playwright                       | 1.x        |
| Code Quality         | ESLint + Prettier                | latest     |
| Type Safety          | TypeScript                       | 5.x        |

______________________________________________________________________

## Options Considered

### Framework Options

#### Option 1: SvelteKit 2.x with Svelte 5 (Chosen)

**Pros:**

- Svelte 5 runes provide fine-grained reactivity with less boilerplate
- Excellent SSR/SSG support for SEO and performance
- Smaller bundle sizes compared to React/Vue
- Native TypeScript support
- Active development and growing ecosystem

**Cons:**

- Smaller ecosystem than React
- Svelte 5 is relatively new (learning curve for runes)
- Fewer third-party component libraries

#### Option 2: Next.js 14+ (React)

**Pros:**

- Largest ecosystem and community
- Extensive third-party component libraries (shadcn/ui, Radix)
- Well-documented patterns for auth, data fetching

**Cons:**

- Larger bundle sizes
- More complex mental model (server components, client components)
- Heavier runtime overhead

#### Option 3: Nuxt 3 (Vue)

**Pros:**

- Good developer experience
- Strong SSR capabilities
- Growing ecosystem

**Cons:**

- Smaller community than React
- Fewer component libraries
- Less alignment with existing architecture decision (SvelteKit)

### Package Manager Options

#### Option 1: pnpm (Chosen)

**Pros:**

- Significantly faster than npm (up to 2x)
- Disk-efficient (content-addressable storage)
- Strict dependency resolution (no phantom dependencies)
- Works well with monorepos

**Cons:**

- Less familiar to some developers
- Occasional compatibility issues with older packages

#### Option 2: npm

**Pros:**

- Universal compatibility
- Default in Node.js ecosystem
- Simple mental model

**Cons:**

- Slower installation times
- Larger disk usage (flat node_modules)

#### Option 3: bun

**Pros:**

- Extremely fast (written in Zig)
- All-in-one runtime, bundler, package manager

**Cons:**

- Experimental/young ecosystem
- Compatibility issues with some packages
- Not as battle-tested in production

### UI Component Library Options

#### Option 1: shadcn-svelte (Chosen)

**Pros:**

- Headless, accessible components (based on Bits UI / Melt UI)
- Full control over styling (copy components into codebase)
- Tailwind CSS integration
- WCAG compliant out of the box
- Active community and documentation

**Cons:**

- Need to copy components (not a package dependency)
- Fewer components than full-featured libraries

#### Option 2: DaisyUI

**Pros:**

- Pre-styled Tailwind components
- Easy to use, fast development
- Large component library

**Cons:**

- Opinionated styling (harder to customize)
- Less accessible by default
- Not headless (tightly coupled to design)

#### Option 3: Build from scratch

**Pros:**

- Full control
- No dependencies

**Cons:**

- Much slower development
- Accessibility requires significant effort
- Reinventing the wheel

### Testing Framework Options

#### Option 1: Vitest + Playwright (Chosen)

**Pros:**

- Vitest: Native ESM, fast, compatible with Vite
- Vitest: Jest-compatible API (easy migration)
- Playwright: Cross-browser E2E testing
- Playwright: Built-in accessibility testing
- Both tools have excellent TypeScript support

**Cons:**

- Two tools to learn/maintain
- Playwright requires browser downloads

#### Option 2: Jest + Cypress

**Pros:**

- Very mature, well-documented
- Large community

**Cons:**

- Jest slower with ESM
- Cypress limited to Chromium-based browsers (free tier)
- Cypress more resource-intensive

______________________________________________________________________

## Consequences

### Positive

- **Fast development**: shadcn-svelte provides accessible components
- **Type safety**: Full TypeScript throughout
- **Performance**: Small bundles, fast page loads
- **Testability**: Comprehensive test coverage with Vitest + Playwright
- **Accessibility**: WCAG compliance from component library
- **Consistency**: Tailwind CSS matches backend documentation styling

### Negative

- **Learning curve**: Svelte 5 runes are new
- **Ecosystem size**: Fewer third-party Svelte packages than React
- **Maintenance**: shadcn-svelte components are copied, not versioned

### Risks

| Risk                                | Likelihood | Impact | Mitigation                                       |
| ----------------------------------- | ---------- | ------ | ------------------------------------------------ |
| Svelte 5 breaking changes           | Low        | Medium | Pin versions; follow migration guides            |
| shadcn-svelte component gaps        | Medium     | Low    | Build custom components as needed                |
| pnpm compatibility issues           | Low        | Low    | Fall back to npm if critical issues arise        |
| Playwright browser download issues  | Low        | Low    | Cache browsers in CI; use npx playwright install |

______________________________________________________________________

## Implementation Notes

### Project Initialization

```bash
# Create SvelteKit project with TypeScript
pnpm create svelte@latest src/frontend
# Select: SvelteKit, TypeScript, ESLint, Prettier, Playwright

# Add Tailwind CSS
cd src/frontend
pnpm add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Add shadcn-svelte
pnpm add -D bits-ui clsx tailwind-merge tailwind-variants
npx shadcn-svelte@latest init

# Add testing dependencies
pnpm add -D vitest @testing-library/svelte jsdom @vitest/coverage-v8
```

### Directory Structure

```
src/frontend/
├── package.json
├── pnpm-lock.yaml
├── svelte.config.js
├── tailwind.config.js
├── vite.config.ts
├── vitest.config.ts
├── playwright.config.ts
├── src/
│   ├── app.html
│   ├── app.css
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn-svelte components
│   │   │   └── __tests__/    # Component tests
│   │   ├── stores/
│   │   └── utils/
│   └── routes/
│       ├── +layout.svelte
│       ├── +page.svelte      # Dashboard
│       ├── login/
│       ├── repositories/
│       └── events/
├── static/
└── tests/
    └── e2e/                  # Playwright tests
```

### Integration with Backend

- Backend API: `http://localhost:8000/api`
- Frontend dev server: `http://localhost:5173`
- Proxy configuration in `vite.config.ts` for development
- Session cookie shared via SameSite policy

______________________________________________________________________

## References

- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Svelte 5 Runes](https://svelte.dev/docs/svelte/what-are-runes)
- [shadcn-svelte](https://shadcn-svelte.com/)
- [Vitest](https://vitest.dev/)
- [Playwright](https://playwright.dev/)
- [pnpm](https://pnpm.io/)

______________________________________________________________________

**Document generated by:** @ui-scaffolder agent

**Related ADRs:**

- [ADR-001: FastAPI + SQLModel](ADR-001-fastapi-sqlmodel.md)
- [ADR-004: uv Package Management](ADR-004-uv-package-management.md)
