# AGENTS.md — Frontend

> Frontend-specific agent guidance. For repo-wide rules, see
> [`../../AGENTS.md`](../../AGENTS.md) and
> [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md).

---

## Status

⚠️ **Frontend not yet implemented.** This folder is a placeholder for future development.

---

## Planned Stack

| Attribute | Value |
|-----------|-------|
| **Framework** | TBD (likely React or Next.js) |
| **Language** | TypeScript |
| **Package Manager** | TBD (likely pnpm or npm) |
| **Testing** | TBD (likely Vitest or Jest) |

---

## When Implementing Frontend

Update this file with:

1. **Environment setup** (Node version, package manager commands)
2. **Development commands** (dev server, build, test, lint)
3. **Directory structure** (components, pages, hooks, utils)
4. **Code patterns** (component creation, state management, API calls)
5. **Testing requirements** (unit tests, integration tests, E2E)
6. **Style guide** (ESLint/Prettier config, naming conventions)

---

## Integration with Backend

The backend API runs at `http://localhost:8000` by default.

Key endpoints to integrate:

- `GET /health` — Health check
- `POST /webhooks/github` — GitHub webhook receiver
- `GET /api/events` — List webhook events
- `GET /api/installations` — List GitHub App installations
- `POST /auth/login` — OAuth login flow
- `POST /auth/logout` — Session logout

See backend API schemas in `../backend/app/api/schemas.py`.

---

## Validation Checklist

When frontend is implemented, add appropriate commands:

```bash
# Placeholder — update when frontend is set up
npm install       # Install dependencies
npm run dev       # Start dev server
npm run build     # Build for production
npm run test      # Run tests
npm run lint      # Lint code
```
