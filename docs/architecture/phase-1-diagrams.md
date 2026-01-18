# Phase 1 System Diagrams

**Agent:** @arch-spec-author

**Date:** January 18, 2026

______________________________________________________________________

## 1. C4 Context Diagram

Shows the system in its environment with external actors and systems.

```mermaid
C4Context
    title System Context Diagram - Copilot Workflow Orchestrator

    Person(developer, "Developer", "Uses the tool to orchestrate Copilot workflows")

    System(orchestrator, "Copilot Workflow Orchestrator", "Webhook-driven automation service for GitHub Copilot workflow management")

    System_Ext(github, "GitHub Platform", "Hosts repositories, issues, PRs, and Copilot")
    System_Ext(github_oauth, "GitHub OAuth", "Authenticates users via OAuth 2.0")
    System_Ext(github_app, "GitHub App", "Receives webhooks and accesses repos via installation tokens")

    Rel(developer, orchestrator, "Views dashboard, manages repos", "HTTPS")
    Rel(orchestrator, github, "Fetches repo data, stores events", "REST API")
    Rel(github, orchestrator, "Sends webhook events", "HTTPS POST")
    Rel(developer, github_oauth, "Authenticates", "OAuth 2.0")
    Rel(github_oauth, orchestrator, "Returns auth token", "OAuth callback")
    Rel(orchestrator, github_app, "Uses installation token", "JWT → Token exchange")
```

______________________________________________________________________

## 2. C4 Container Diagram

Shows the high-level technical building blocks.

```mermaid
C4Container
    title Container Diagram - Copilot Workflow Orchestrator

    Person(developer, "Developer", "Uses browser to access the tool")

    Container_Boundary(orchestrator, "Copilot Workflow Orchestrator") {
        Container(frontend, "SvelteKit Frontend", "SvelteKit, Tailwind CSS", "Dashboard UI, event viewer, repo management")
        Container(backend, "FastAPI Backend", "Python, FastAPI, SQLModel", "REST API, webhook handler, auth service")
        ContainerDb(database, "Database", "PostgreSQL / SQLite", "Stores users, sessions, events, repos")
    }

    System_Ext(github, "GitHub Platform", "Webhooks, REST API, OAuth")

    Rel(developer, frontend, "Uses", "HTTPS")
    Rel(frontend, backend, "API calls", "REST/JSON")
    Rel(github, backend, "Webhooks", "HTTPS POST + HMAC")
    Rel(backend, github, "API requests", "REST + Installation Token")
    Rel(backend, database, "Reads/Writes", "SQLModel/SQLAlchemy")
```

______________________________________________________________________

## 3. Component Diagram (Backend)

Shows the internal structure of the FastAPI backend.

```mermaid
flowchart TB
    subgraph FastAPI Backend
        subgraph API Layer
            webhook["/api/webhooks/github<br>Webhook Receiver"]
            auth_routes["/api/auth/*<br>OAuth Routes"]
            repo_routes["/api/repos/*<br>Repository Routes"]
            event_routes["/api/events/*<br>Event Routes"]
            health["/health<br>Health Check"]
        end

        subgraph Services
            auth_service["AuthService<br>OAuth + Sessions"]
            webhook_service["WebhookService<br>Signature + Processing"]
            event_service["EventService<br>Storage + Query"]
            repo_service["RepoService<br>Installation + Repos"]
            github_client["GitHubClient<br>API Wrapper"]
        end

        subgraph Data Layer
            models["SQLModel Models<br>User, Session, Event, Repo"]
            db["Database Engine<br>PostgreSQL / SQLite"]
        end
    end

    webhook --> webhook_service
    auth_routes --> auth_service
    repo_routes --> repo_service
    event_routes --> event_service
    health --> db

    auth_service --> models
    webhook_service --> event_service
    webhook_service --> github_client
    event_service --> models
    repo_service --> github_client
    repo_service --> models

    models --> db
    github_client --> GitHub[(GitHub API)]
```

______________________________________________________________________

## 4. Sequence Diagram: OAuth Login Flow

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Frontend as SvelteKit Frontend
    participant Backend as FastAPI Backend
    participant GitHub as GitHub OAuth

    Browser->>Frontend: Visit /login
    Frontend->>Browser: Render login page

    Browser->>Frontend: Click "Login with GitHub"
    Frontend->>Backend: GET /api/auth/login
    Backend->>Backend: Generate state token (CSRF)
    Backend->>Browser: Redirect to GitHub OAuth URL

    Browser->>GitHub: Authorization request
    GitHub->>Browser: Show consent screen
    Browser->>GitHub: User approves

    GitHub->>Browser: Redirect to /api/auth/callback?code=XXX&state=YYY
    Browser->>Backend: GET /api/auth/callback?code=XXX&state=YYY

    Backend->>Backend: Validate state token
    Backend->>GitHub: POST /login/oauth/access_token (exchange code)
    GitHub->>Backend: Return access_token

    Backend->>GitHub: GET /user (fetch user profile)
    GitHub->>Backend: Return user data

    Backend->>Backend: Create/update User record
    Backend->>Backend: Create Session record
    Backend->>Browser: Set session cookie + Redirect to /dashboard

    Browser->>Frontend: Load dashboard
    Frontend->>Backend: GET /api/repos (with session cookie)
    Backend->>Backend: Validate session
    Backend->>Frontend: Return user's repositories
    Frontend->>Browser: Render dashboard
```

______________________________________________________________________

## 5. Sequence Diagram: GitHub App Installation

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Backend as FastAPI Backend
    participant GitHub as GitHub Platform

    Browser->>Backend: GET /api/installations/new
    Backend->>Browser: Redirect to GitHub App install URL

    Browser->>GitHub: Install GitHub App
    GitHub->>Browser: Select repositories
    Browser->>GitHub: Confirm installation

    GitHub->>Browser: Redirect to /api/installations/callback?installation_id=123

    Browser->>Backend: GET /api/installations/callback?installation_id=123
    Backend->>Backend: Generate JWT (signed with App private key)
    Backend->>GitHub: POST /app/installations/123/access_tokens
    GitHub->>Backend: Return installation_access_token

    Backend->>GitHub: GET /installation/repositories
    GitHub->>Backend: Return list of accessible repos

    Backend->>Backend: Store Installation + Repositories
    Backend->>Browser: Redirect to /dashboard

    Note over Backend,GitHub: Installation token cached (1 hour expiry)
```

______________________________________________________________________

## 6. Sequence Diagram: Webhook Reception

```mermaid
sequenceDiagram
    autonumber
    participant GitHub
    participant Backend as FastAPI Backend
    participant DB as Database

    GitHub->>Backend: POST /api/webhooks/github<br>Headers: X-Hub-Signature-256, X-GitHub-Delivery

    Backend->>Backend: Extract signature from header
    Backend->>Backend: Compute HMAC-SHA256 of body
    Backend->>Backend: Compare signatures (timing-safe)

    alt Signature Invalid
        Backend->>Backend: Log failed verification
        Backend->>GitHub: 401 Unauthorized
    end

    Backend->>Backend: Parse JSON payload
    Backend->>Backend: Extract: event_type, action, delivery_id

    Backend->>DB: Check if delivery_id exists (dedup)

    alt Duplicate Event
        Backend->>Backend: Log "duplicate ignored"
        Backend->>GitHub: 200 OK (idempotent)
    end

    Backend->>DB: INSERT EventReceipt

    Backend->>GitHub: 200 OK

    Note over Backend: Event stored synchronously<br>(async queue in Phase 3+)
```

______________________________________________________________________

## 7. Sequence Diagram: Event Stream Query

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Frontend as SvelteKit Frontend
    participant Backend as FastAPI Backend
    participant DB as Database

    Browser->>Frontend: Navigate to /repos/{repo_id}/events
    Frontend->>Backend: GET /api/repos/{repo_id}/events?page=1&limit=50

    Backend->>Backend: Validate session cookie
    Backend->>Backend: Check user owns repo

    alt Unauthorized
        Backend->>Frontend: 401 Unauthorized
        Frontend->>Browser: Redirect to /login
    end

    Backend->>DB: SELECT events WHERE repo_id = X<br>ORDER BY received_at DESC<br>LIMIT 50 OFFSET 0

    DB->>Backend: Return events (paginated)

    Backend->>Frontend: 200 OK + JSON array of events

    Frontend->>Browser: Render event stream list

    Note over Browser: User can filter by event_type, date range
```

______________________________________________________________________

## 8. Deployment Diagram

```mermaid
flowchart TB
    subgraph Development
        dev_sqlite[(SQLite)]
        dev_backend[FastAPI<br>uvicorn --reload]
        dev_frontend[SvelteKit<br>npm run dev]
        dev_backend --> dev_sqlite
    end

    subgraph Production [Docker Compose]
        subgraph docker_network[Docker Network]
            prod_frontend[SvelteKit Container<br>Node.js]
            prod_backend[FastAPI Container<br>Uvicorn + Gunicorn]
            prod_db[(PostgreSQL Container)]
        end

        prod_frontend --> prod_backend
        prod_backend --> prod_db
    end

    subgraph External
        github[GitHub Platform]
        user[Developer Browser]
    end

    github -->|Webhooks| prod_backend
    user -->|HTTPS| prod_frontend
    prod_backend -->|API calls| github
```

______________________________________________________________________

## 9. Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ UserSession : has
    User ||--o{ Installation : owns
    Installation ||--o{ InstallationRepository : contains
    InstallationRepository }o--|| Repository : references
    Repository ||--o{ EventReceipt : receives

    User {
        uuid id PK
        int github_id UK
        string username
        string email
        string avatar_url
        string access_token
        datetime created_at
        datetime updated_at
    }

    UserSession {
        uuid id PK
        uuid user_id FK
        string session_token UK
        datetime expires_at
        datetime last_activity_at
        string ip_address
        string user_agent
        datetime created_at
    }

    Installation {
        uuid id PK
        int installation_id UK
        uuid user_id FK
        string account_login
        string account_type
        json permissions
        bool is_suspended
        datetime suspended_at
        datetime created_at
        datetime updated_at
    }

    InstallationRepository {
        uuid id PK
        uuid installation_id FK
        uuid repository_id FK
        datetime created_at
    }

    Repository {
        uuid id PK
        int github_id UK
        string owner
        string name
        string full_name
        string description
        string url
        bool is_private
        string default_branch
        datetime last_event_at
        int event_count
        datetime created_at
        datetime updated_at
    }

    EventReceipt {
        uuid id PK
        string delivery_id UK
        uuid installation_id FK
        uuid repository_id FK
        string event_type
        string event_action
        string actor
        json target_object_ids
        datetime received_at
        datetime github_timestamp
        json raw_payload
        string processing_status
        string error_message
        int retry_count
        datetime created_at
        datetime updated_at
    }
```

______________________________________________________________________

**Diagrams generated by:** @arch-spec-author agent
