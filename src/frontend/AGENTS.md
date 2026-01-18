# AGENTS.md — Frontend

> Frontend-specific agent guidance. For repo-wide rules, see
> [`../../AGENTS.md`](../../AGENTS.md) and
> [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md).

---

## Status

🔄 **Frontend scaffolding in progress.** Stack finalized, implementation starting.

---

## Finalized Stack

| Attribute           | Value                            |
| ------------------- | -------------------------------- |
| **Framework**       | SvelteKit 2.x (Svelte 5)         |
| **Language**        | TypeScript 5.x                   |
| **Package Manager** | pnpm                             |
| **CSS Framework**   | Tailwind CSS 3.x                 |
| **UI Components**   | shadcn-svelte                    |
| **Unit Testing**    | Vitest + @testing-library/svelte |
| **E2E Testing**     | Playwright                       |
| **Code Quality**    | ESLint + Prettier                |

---

## Build & Validation Commands

**All commands run from repository root.** Use the Makefile; do not run pnpm directly.

### Required Setup (run once)

```bash
make frontend-install           # Install all dependencies
make frontend-install-browsers  # Install browser binaries for E2E tests
```

### Development Workflow

| Task                     | Command                  |
| ------------------------ | ------------------------ |
| **Start dev server**     | `make frontend-dev`      |
| **Run unit tests**       | `make frontend-test`     |
| **Run tests with UI**    | `make frontend-test-ui`  |
| **Run E2E tests**        | `make frontend-test-e2e` |
| **Run all tests**        | `make frontend-test-all` |
| **Type check**           | `make frontend-check`    |
| **Lint code**            | `make frontend-lint`     |
| **Format code**          | `make frontend-format`   |
| **Build for production** | `make frontend-build`    |
| **Preview production**   | `make frontend-preview`  |

### Validation Before Committing

**ALWAYS run these before declaring work complete:**

```bash
make frontend-check      # TypeScript type checking
make frontend-lint       # ESLint checks
make frontend-test       # Unit/component tests
make frontend-test-e2e   # E2E tests (if UI changes)
```

---

## Directory Structure

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
│   ├── app.css                  # Global styles, Tailwind imports
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn-svelte components
│   │   │   └── __tests__/       # Component unit tests
│   │   ├── stores/              # Svelte stores (auth, etc.)
│   │   │   └── __tests__/
│   │   └── utils/               # Utility functions
│   │       └── __tests__/
│   └── routes/
│       ├── +layout.svelte       # Root layout
│       ├── +page.svelte         # Dashboard (home)
│       ├── login/
│       │   └── +page.svelte
│       ├── repositories/
│       │   ├── +page.svelte     # Repository list
│       │   └── [id]/
│       │       └── +page.svelte # Repository detail
│       └── events/
│           ├── +page.svelte     # Event list
│           └── [id]/
│               └── +page.svelte # Event detail
├── static/                      # Static assets
└── tests/
    └── e2e/                     # Playwright E2E tests
        ├── login.spec.ts
        ├── dashboard.spec.ts
        ├── events.spec.ts
        └── repositories.spec.ts
```

---

## Code Patterns

### Component Creation

```typescript
<!-- src/lib/components/EventCard.svelte -->
<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';
  import type { Event } from '$lib/types';

  interface Props {
    event: Event;
    showRawPayload?: boolean;
  }

  let { event, showRawPayload = false }: Props = $props();

  // Derived state using Svelte 5 runes
  let formattedDate = $derived(
    new Date(event.created_at).toLocaleString()
  );
</script>

<div data-testid="event-card" class="p-4 border rounded-lg">
  <Badge>{event.event_type}</Badge>
  <span>{formattedDate}</span>
</div>
```

### Store Pattern (Svelte 5)

```typescript
// src/lib/stores/auth.svelte.ts
import type { User } from '$lib/types';

class AuthStore {
	user = $state<User | null>(null);
	isLoading = $state(true);

	get isAuthenticated() {
		return this.user !== null;
	}

	async fetchUser() {
		this.isLoading = true;
		try {
			const res = await fetch('/api/auth/me');
			if (res.ok) {
				this.user = await res.json();
			}
		} finally {
			this.isLoading = false;
		}
	}

	logout() {
		this.user = null;
	}
}

export const auth = new AuthStore();
```

### Component Testing

```typescript
// src/lib/components/__tests__/EventCard.test.ts
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import EventCard from '../EventCard.svelte';

describe('EventCard', () => {
	it('renders event type badge', () => {
		const event = {
			id: '1',
			event_type: 'pull_request',
			created_at: '2026-01-18T10:00:00Z'
		};

		render(EventCard, { props: { event } });

		expect(screen.getByText('pull_request')).toBeInTheDocument();
	});
});
```

---

## Integration with Backend

The backend API runs at `http://localhost:8000` by default.

### API Proxy (Development)

Configure in `vite.config.ts`:

```typescript
export default defineConfig({
	server: {
		proxy: {
			'/api': 'http://localhost:8000'
		}
	}
});
```

### Key Endpoints

| Endpoint                 | Description             |
| ------------------------ | ----------------------- |
| `GET /api/health`        | Health check            |
| `GET /api/auth/login`    | Initiate OAuth flow     |
| `GET /api/auth/callback` | OAuth callback          |
| `GET /api/auth/me`       | Current user            |
| `POST /api/auth/logout`  | Logout                  |
| `GET /api/installations` | List installations      |
| `GET /api/events`        | List events (paginated) |

See backend API schemas in `../backend/app/api/schemas.py`.

---

## Testing Requirements

### Unit/Component Tests (Vitest)

- **Target coverage**: 80%+ for components
- **Location**: `src/lib/components/__tests__/`
- **Naming**: `ComponentName.test.ts`
- **Run**: `make frontend-test`

### E2E Tests (Playwright)

- **Location**: `tests/e2e/`
- **Naming**: `feature.spec.ts`
- **Run**: `make frontend-test-e2e`
- **Critical paths**:
    - Login → Dashboard flow
    - Dashboard → Repository detail
    - Event stream navigation

---

## Accessibility Requirements

All components must:

- [x] Support keyboard navigation
- [x] Have proper ARIA labels
- [x] Meet WCAG AA color contrast
- [x] Announce route changes to screen readers

shadcn-svelte components provide accessibility by default.

---

## References

- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Svelte 5 Runes](https://svelte.dev/docs/svelte/what-are-runes)
- [shadcn-svelte](https://shadcn-svelte.com/)
- [ADR-005: Frontend Stack](../../docs/architecture/adr/ADR-005-frontend-stack.md)
