# Phase 1 User Stories — Copilot Workflow Orchestrator

**Status:** Story Building Complete — Ready for Validation

**Date:** January 17, 2026

**Agent:** @story-builder

**Phase:** Phase 1 (Event Stream + Dashboard + Authentication)

______________________________________________________________________

## Story 0: User Authentication (OAuth Login)

**User Story:**

> As a **developer**, I want to **log in with my GitHub account**, so that **I
> can access the tool securely and manage my own repositories**.

**Acceptance Criteria:**

```gherkin
Scenario: User visits the tool for the first time
  Given I have not logged in before
  When I visit the home page (https://orchestrator.example.com/)
  Then I am redirected to the login page
  And I see a "Login with GitHub" button
  And I see the tool name and description

Scenario: User logs in with GitHub (OAuth flow)
  Given I am on the login page
  When I click "Login with GitHub"
  Then I am redirected to GitHub OAuth authorization page
  And the URL includes: client_id, redirect_uri, scope (user:email, read:user)

  When I authorize the app on GitHub
  Then I am redirected back to: https://orchestrator.example.com/callback?code=ABC123
  And the tool exchanges the code for a user access token
  And a session is created for me (HTTP-only cookie, secure)
  And I am redirected to the dashboard (home page)

Scenario: User is already logged in
  Given I have logged in previously
  And my session is still valid
  When I visit the home page
  Then I see the dashboard directly (no login page)
  And I do not need to re-authenticate

Scenario: Session expires after inactivity
  Given I have logged in previously
  And my session has expired (>30 days old or logged out)
  When I visit the home page
  Then I am redirected to the login page
  And a message says "Session expired. Please login again."

Scenario: User logs out
  Given I am logged in
  When I click "Logout" in the user menu
  Then my session is destroyed
  And I am redirected to the login page
  And a success message says "You have been logged out"

Scenario: OAuth callback with error
  Given I am attempting to log in with GitHub
  When GitHub returns an error (e.g., user denies authorization)
  Then I am redirected to the login page
  And an error message is displayed: "Authorization failed. Please try again."
  And the error details are logged (not shown to user)

Scenario: OAuth token exchange fails
  Given I have authorized the app on GitHub
  When the tool attempts to exchange the code for a token
  And the GitHub API returns an error
  Then I see an error message: "Login failed. Please try again later."
  And the error is logged for debugging
  And I am not logged in

Scenario: View user profile after login
  Given I am logged in
  When I visit the user menu
  Then I see my GitHub username and avatar
  And I see options: "Dashboard", "Settings", "Logout"
```

**Definition of Ready:**

- [x] GitHub App OAuth credentials are configured (Client ID, Client Secret)
- [x] OAuth callback URL is registered:
  `https://orchestrator.example.com/callback`
- [x] Session storage mechanism is chosen (PostgreSQL session table via
  SQLModel)
- [x] Session expiration policy is defined (30 days, refresh on activity)
- [x] HTTPS is enforced (OAuth requires secure connections)
- [x] CSRF protection is implemented
- [x] FastAPI OAuth2 integration is documented

**Data Model:**

```yaml
User:
  id: UUID (primary key)
  github_id: Integer (GitHub user ID, unique)
  username: String (GitHub username)
  email: String (from GitHub, nullable)
  avatar_url: String (GitHub profile picture)
  access_token: String (encrypted, for user identity)
  access_token_expires_at: DateTime (nullable)
  created_at: DateTime
  updated_at: DateTime

UserSession:
  id: UUID (primary key)
  user_id: Foreign Key → User
  session_token: String (hashed, unique)
  expires_at: DateTime
  last_activity_at: DateTime
  ip_address: String (for security audit)
  user_agent: String (browser info)
  created_at: DateTime
```

**Out of Scope:**

- Multi-factor authentication (MFA) — deferred to Phase 6+
- OAuth refresh token flow (access tokens are long-lived for GitHub Apps)
- Social login (only GitHub supported)

**Estimated Effort:** 3-4 days (OAuth flow + session management + security)

**Dependencies:** None (foundational story)

______________________________________________________________________

## Story 0b: App Installation & Repository Access

**User Story:**

> As a **logged-in user**, I want to **install the GitHub App on my
> repositories**, so that **the tool can receive webhooks and orchestrate my
> Copilot workflows**.

**Acceptance Criteria:**

```gherkin
Scenario: User has no repositories connected (first-time setup)
  Given I am logged in
  And I have not installed the GitHub App yet
  When I visit the dashboard
  Then I see an empty state message: "No repositories connected yet"
  And I see a "Connect Repositories" button
  And I see instructions: "Click to install the GitHub App and select repositories"

Scenario: User installs the GitHub App
  Given I am on the dashboard (empty state)
  When I click "Connect Repositories"
  Then I am redirected to GitHub App installation page:
       https://github.com/apps/copilot-orchestrator/installations/new

  When I select repositories (e.g., user/repo1, user/repo2)
  And I click "Install"
  Then GitHub redirects back to:
       https://orchestrator.example.com/setup?installation_id=12345&setup_action=install
  And the tool receives the installation callback
  And the tool generates an installation access token (JWT-based)
  And the tool fetches the list of repositories from GitHub API
  And the tool stores: installation_id, user_id, [repo1, repo2]
  And I am redirected to the dashboard
  And I see my connected repositories

Scenario: User updates repository selection
  Given I have already installed the GitHub App
  When I click "Manage Repositories" in settings
  Then I am redirected to GitHub App installation settings:
       https://github.com/settings/installations/12345

  When I add or remove repositories
  And I click "Save"
  Then GitHub redirects back to:
       https://orchestrator.example.com/setup?installation_id=12345&setup_action=install
  And the tool re-fetches the repository list
  And my dashboard is updated with the new repository list

Scenario: User suspends the GitHub App installation
  Given I have installed the GitHub App
  When I suspend the installation on GitHub
  Then GitHub sends a webhook: installation.suspended
  And the tool marks the installation as suspended
  And my dashboard shows: "Installation suspended. Please reactivate on GitHub."
  And webhooks are not processed for suspended repositories

Scenario: User uninstalls the GitHub App
  Given I have installed the GitHub App
  When I uninstall the app on GitHub
  Then GitHub sends a webhook: installation.deleted
  And the tool marks the installation as deleted
  And my dashboard shows an empty state again
  And webhook data is retained (for audit/debugging)

Scenario: Installation callback fails
  Given I have installed the GitHub App on GitHub
  When the tool receives the installation callback
  And the GitHub API fails to return repository details
  Then I see an error: "Failed to connect repositories. Please try again."
  And a "Retry" button is shown
  And the error is logged

Scenario: Tool generates installation access token
  Given an installation_id has been received
  When the tool needs to call GitHub API on behalf of the installation
  Then the tool generates a JWT (signed with GitHub App private key)
  And exchanges the JWT for an installation access token
  And the installation access token is cached (expires in 1 hour)
  And the token is refreshed automatically when expired

Scenario: Single installation per user (Phase 1 constraint)
  Given I have one installation already
  When I attempt to create a second installation
  Then the tool shows a message: "Only one installation per user is supported in this version"
  And I am redirected to manage my existing installation
```

**Definition of Ready:**

- [x] GitHub App is registered and credentials are available
- [x] GitHub App private key is securely stored
- [x] JWT generation library is chosen (PyJWT)
- [x] GitHub API endpoints are documented (list installations, get installation
  repos)
- [x] Webhook for installation events is subscribed
- [x] Database schema for Installation entity is designed (SQLModel)

**Data Model:**

```yaml
Installation:
  id: UUID (primary key)
  installation_id: Integer (GitHub installation ID, unique)
  user_id: Foreign Key → User
  account_login: String (GitHub username or org name)
  account_type: String (User or Organization)
  target_type: String (User or Organization)
  permissions: JSON (granted permissions snapshot)
  events: JSON (subscribed webhook events)
  is_suspended: Boolean (default: false)
  suspended_at: DateTime (nullable)
  created_at: DateTime
  updated_at: DateTime

InstallationRepository:
  id: UUID (primary key)
  installation_id: Foreign Key → Installation
  repository_id: Foreign Key → Repository
  created_at: DateTime
```

**Out of Scope:**

- Multiple installations per user (deferred to Phase 6+ multi-tenant)
- Organization-level installations with team permissions

**Estimated Effort:** 4-5 days (installation flow + JWT handling + GitHub API
integration)

**Dependencies:** Story 0 (user must be logged in first)

______________________________________________________________________

## Story 1: GitHub App Webhook Receiver

**User Story:**

> As a **tool operator**, I want the tool to **receive and verify GitHub
> webhooks**, so that **I can trust that incoming events are authentic and not
> forged**.

**Acceptance Criteria:**

```gherkin
Scenario: Successfully receive and verify a valid webhook
  Given the tool is running with a valid GitHub App secret configured
  And a repository is connected (Story 0b)
  When GitHub sends a webhook with a valid HMAC-SHA256 signature
  Then the tool returns HTTP 200 OK
  And the webhook event is queued for processing
  And the delivery ID is recorded for deduplication

Scenario: Reject webhook with invalid signature
  Given the tool is running with a valid GitHub App secret
  When GitHub sends a webhook with an invalid signature
  Then the tool returns HTTP 401 Unauthorized
  And the event is NOT processed
  And the failed attempt is logged with timestamp and source IP

Scenario: Reject webhook when secret is misconfigured
  Given the tool is running with an incorrect GitHub App secret
  When GitHub sends a valid webhook
  Then the tool returns HTTP 401 Unauthorized
  And the event is logged to an error queue (for manual investigation)
  And an alert is triggered (email or dashboard notification)

Scenario: Handle webhook retries without duplicate processing
  Given a webhook event has been processed successfully
  When GitHub redelivers the same event (same delivery ID)
  Then the tool returns HTTP 200 OK
  And the event is marked as duplicate (not reprocessed)
  And a log entry notes: "Duplicate webhook ignored"

Scenario: Handle malformed webhook payload gracefully
  Given the tool is running
  When GitHub sends a webhook with invalid JSON payload
  Then the tool returns HTTP 400 Bad Request
  And the raw payload is stored for debugging (up to 1MB)
  And an error is logged with context (event type, delivery ID)

Scenario: Timeout handling for slow webhook processing
  Given the tool is processing a large webhook (e.g., large PR diff summary)
  When processing takes >30 seconds
  Then the tool returns HTTP 202 Accepted to GitHub immediately
  And continues processing asynchronously in a background queue
  And the event is retryable if async processing fails

Scenario: Only process webhooks for connected repositories
  Given a repository is NOT connected to the tool
  When GitHub sends a webhook for that repository
  Then the tool returns HTTP 200 OK (to avoid GitHub retries)
  And the event is logged but NOT processed
  And a note is added: "Webhook from unconnected repo, ignored"
```

**Definition of Ready:**

- [x] GitHub App webhook secret is configured and stored securely
- [x] Webhook signature verification algorithm (HMAC-SHA256) is documented
- [x] Expected webhook event payloads are documented
- [x] Error handling strategy is defined (fail-closed, log details)
- [x] Deduplication strategy (delivery ID) is designed
- [x] Database schema for event storage is sketched (Story 2)

**Out of Scope:**

- Processing/interpreting the webhook payload (that's Story 2)
- Retrying failed deliveries to GitHub (GitHub owns retries)

**Estimated Effort:** 3-5 days (includes signature verification, idempotency,
error handling)

**Dependencies:** Story 0b (installation must be set up)

______________________________________________________________________

## Story 2: Event Stream Storage (Database)

**User Story:**

> As a **tool operator**, I want the tool to **persist webhook events to a
> database**, so that **I can view the complete event history and debug
> issues**.

**Acceptance Criteria:**

```gherkin
Scenario: Store a valid webhook event
  Given a webhook event has been verified (Story 1)
  When the event is queued for processing
  Then the event is stored in the database with:
    - Event ID (UUID, unique)
    - Delivery ID (from GitHub, for deduplication)
    - Repository (owner/repo)
    - Installation ID (for multi-tenant isolation)
    - Event type (e.g., "pull_request")
    - Event action (e.g., "opened")
    - Actor (GitHub user/bot who triggered event)
    - Target object IDs (issue number, PR number, etc.)
    - Received timestamp (tool time)
    - GitHub timestamp (event creation time from payload)
    - Raw payload (JSON, compressed if >100KB)
    - Processing status (received/processing/processed/failed)

Scenario: Store event with GitHub timestamp
  Given a webhook event includes a GitHub timestamp
  When the event is stored
  Then both received_timestamp (tool) and github_timestamp (GitHub) are stored
  And timestamps are stored in UTC with timezone info

Scenario: Handle concurrent event inserts
  Given multiple webhooks are received simultaneously
  When they are inserted into the database
  Then all events are stored without data loss
  And the database maintains referential integrity
  And no race conditions occur (pessimistic locking or unique constraints)

Scenario: Query event history by repository
  Given events have been stored for multiple repositories
  When a user queries events for "owner/repo"
  Then all events for that repo are returned in reverse chronological order
  And pagination is supported (limit/offset or cursor-based)

Scenario: Deduplication on insert
  Given a webhook event with delivery ID X has been stored
  When the same event (delivery ID X) is inserted again
  Then the database rejects the duplicate (unique constraint)
  And the original event record is unchanged
  And a log entry notes: "Duplicate event insert prevented"

Scenario: Handle payload that exceeds database limits
  Given a webhook payload is extremely large (>1MB)
  When the event is stored
  Then the payload is compressed (gzip) before storage
  And if still too large, the payload is stored in object storage (S3/GCS)
  And the event record includes a reference to the external payload
  And the event metadata is always queryable

Scenario: Database connectivity failure
  Given the database is temporarily unavailable
  When a webhook is received
  Then the event is queued in memory (or Redis dead-letter queue)
  And a health alert is triggered
  And processing is retried when database is available (exponential backoff)
  And no events are lost (durable queue)

Scenario: Query events by user (isolation)
  Given multiple users have connected repositories
  When User A queries their events
  Then only events from User A's connected repositories are returned
  And User A cannot see User B's events (security isolation)
```

**Definition of Ready:**

- [x] Database schema is designed (Entity Relationship Diagram provided)
- [x] Indexing strategy is defined (by repo, by event_type, by timestamp, by
  user)
- [x] Retention policy is documented (1 year, then archive/delete)
- [x] Connection pooling strategy is chosen
- [x] Backup/recovery procedure is sketched
- [x] SQLite (dev) and PostgreSQL (prod) schemas are compatible (SQLModel)

**Data Model:**

```yaml
EventReceipt:
  id: UUID (primary key)
  delivery_id: String (GitHub delivery ID, unique)
  installation_id: Foreign Key → Installation
  repository_id: Foreign Key → Repository
  event_type: String (issues, pull_request, check_suite, etc.)
  event_action: String (opened, closed, synchronize, etc.)
  actor: String (GitHub username/bot name)
  target_object_ids: JSON (issue_number, pr_number, check_run_id, etc.)
  received_timestamp: DateTime (tool received time, indexed)
  github_timestamp: DateTime (GitHub event time)
  raw_payload: JSONB or TEXT (full webhook payload, compressed if large)
  payload_storage: String (database or external URL if >1MB)
  processing_status: Enum (received, processing, processed, failed)
  error_message: Text (if processing failed)
  retry_count: Integer (default: 0)
  created_at: DateTime
  updated_at: DateTime
```

**Out of Scope:**

- Processing the event (that's subsequent stories)
- Data warehousing/analytics (future phase)

**Estimated Effort:** 3-5 days (schema design, migrations, indexing, testing)

**Dependencies:** Story 1 (webhook receiver must be working), Story 0b
(installation)

______________________________________________________________________

## Story 3: Repository Selection UI

**User Story:**

> As a **logged-in user**, I want to **view and manage my connected
> repositories**, so that **I can control which repositories the tool
> monitors**.

**Acceptance Criteria:**

```gherkin
Scenario: View list of connected repositories
  Given I am logged in
  And I have installed the GitHub App (Story 0b)
  When I visit the dashboard or repository settings page
  Then I see a list of all my connected repositories
  And each repository shows:
    - Repository name (owner/repo)
    - Description (from GitHub)
    - Last event received timestamp (or "no events yet")
    - Event count (total events received)
    - A "View Detail" link (navigates to event stream)

Scenario: Search for a repository
  Given I am viewing a long list of repositories (10+ repos)
  When I type in a search box
  Then the list is filtered by repository name (real-time)
  And matching repositories are highlighted

Scenario: Disconnect a repository
  Given I am viewing my connected repositories
  When I click "Disconnect" or "Remove" on a repository
  Then a confirmation dialog is shown: "Are you sure? Past events will be retained."

  When I confirm
  Then I am redirected to GitHub App installation settings
  And I can remove the repository there
  And the repository is no longer shown in my dashboard (after GitHub callback)

Scenario: View repository health
  Given repositories are connected
  When I view the repository list
  Then each repository shows a health indicator:
    - Green: Events received recently (<1 hour)
    - Yellow: No events in last 24 hours (warning)
    - Red: Webhook errors detected or installation suspended

Scenario: Handle GitHub API errors
  Given the tool is attempting to fetch the repository list
  When GitHub API is unavailable or rate-limited
  Then an error message is displayed: "Failed to load repositories. Please try again."
  And a "Retry" button is provided
  And the last cached repository list is shown (if available)

Scenario: Empty state (no repositories connected)
  Given I am logged in
  And I have not installed the GitHub App yet
  When I visit the dashboard
  Then I see: "No repositories connected yet"
  And I see a "Connect Repositories" button (Story 0b)
  And I see helpful instructions
```

**Definition of Ready:**

- [x] SvelteKit project is initialized with Tailwind CSS
- [x] GitHub API endpoint for listing installation repositories is documented
- [x] UI wireframes/mockups are approved
- [x] Database schema for Repository entity is designed (SQLModel)
- [x] Authentication middleware is working (Story 0)

**Data Model:**

```yaml
Repository:
  id: UUID (primary key)
  github_id: Integer (GitHub repository ID, unique)
  owner: String (GitHub username or org)
  name: String (repository name)
  full_name: String (owner/repo, indexed)
  description: String (from GitHub, nullable)
  url: String (GitHub URL)
  is_private: Boolean (from GitHub)
  default_branch: String (main, master, etc.)
  last_event_received_at: DateTime (nullable, indexed)
  event_count: Integer (cached count, default: 0)
  created_at: DateTime
  updated_at: DateTime
```

**Out of Scope:**

- Webhook configuration in GitHub UI (GitHub handles this automatically)
- Multi-user permissions (all connected users see their own repos only)

**Estimated Effort:** 2-4 days (SvelteKit UI + GitHub API integration)

**Dependencies:** Story 0b (installation must exist), Story 2 (event count
query)

______________________________________________________________________

## Story 4: Event Stream Viewer

**User Story:**

> As a **tool operator**, I want to **view a complete timeline of webhook
> events** for each repository, so that **I can debug issues and understand
> workflow state changes**.

**Acceptance Criteria:**

```gherkin
Scenario: View recent events on home page (dashboard)
  Given I am logged in
  And I have connected repositories with events
  When I visit the dashboard (home page)
  Then I see the last 10 webhook events across all my repositories
  And each event shows:
    - Timestamp (received)
    - Event type and action (e.g., "pull_request: opened")
    - Repository (owner/repo)
    - Actor (GitHub user/bot)
    - Target object (issue #5, PR #10, etc.) with link to GitHub
    - Processing status badge (received/processing/processed/failed)

Scenario: View detailed event stream per repository
  Given I am viewing a repository
  When I click "View Events" or navigate to the repository detail page
  Then I see the detailed event stream for that repository only
  And events are displayed in reverse chronological order (newest first)
  And pagination/infinite scroll is supported (load more)
  And I can see ~50 events per page

Scenario: Filter events by type
  Given I am viewing the event stream
  When I select a filter dropdown (e.g., "pull_request" only)
  Then the stream shows only matching event types
  And the filter selection persists as I navigate (query parameter)

Scenario: Filter events by time range
  Given I am viewing the event stream
  When I select a date range picker (e.g., "last 7 days")
  Then only events within that range are displayed
  And the date picker is intuitive (calendar UI or text input)

Scenario: Search for a specific event
  Given I am viewing the event stream (many events)
  When I type a search query (e.g., "issue #5" or "@copilot")
  Then events matching the query are highlighted or filtered
  And search works on: issue/PR numbers, actor names, event actions

Scenario: View raw event payload
  Given I am viewing an event in the stream
  When I click "View Raw Payload" or expand the event
  Then a read-only JSON viewer is displayed (syntax-highlighted)
  And the payload is formatted for readability (indented)
  And I can copy the payload to clipboard (copy button)

Scenario: Event stream performance with 1 year of events
  Given there are 50,000+ events in the database (1 year @ ~150 events/day per repo)
  When I visit the event stream page
  Then it loads in <3 seconds
  And pagination works smoothly (no lag)
  And database queries are efficient (indexed searches)

Scenario: Real-time event updates (optional nice-to-have)
  Given I am viewing the event stream
  When a new webhook event is received
  Then the event appears at the top of the stream (after ~5-10 seconds)
  And a subtle "new event" badge is shown
  And the page does not require a manual refresh (polling or SSE)

Scenario: Handle no events
  Given I am viewing a repository with no events yet
  When I visit the event stream page
  Then a "No events yet" message is displayed
  And I see a hint: "Trigger an event by creating an issue or PR in this repository"
```

**Definition of Ready:**

- [x] Event table schema is finalized (Story 2)
- [x] Indexing strategy is designed (event_type, repository, timestamp)
- [x] UI wireframes are approved
- [x] Pagination strategy is chosen (limit/offset vs. cursor-based)
- [x] Real-time update mechanism is decided (polling, WebSocket, or SSE)

**Out of Scope:**

- Event processing/interpretation (separate stories)
- Alerting on specific events (Phase 5+)

**Estimated Effort:** 4-6 days (SvelteKit UI + pagination + search + performance
optimization)

**Dependencies:** Stories 0b-2 (auth, installation, event storage must be
working), Story 3 (repo list)

______________________________________________________________________

## Story 5: Minimal Dashboard

**User Story:**

> As a **tool operator**, I want to **see a dashboard showing the current state
> of each repository**, so that **I can quickly understand what's happening and
> identify blockers**.

**Acceptance Criteria:**

```gherkin
Scenario: View dashboard with multiple connected repositories
  Given I am logged in
  And I have connected repositories with events
  When I visit the dashboard (home page)
  Then I see a list/grid of all my connected repositories
  And for each repository, I see:
    - Repository name (clickable → detail page)
    - Current status (idle / active / blocked / error)
    - Current active issue (if any): number + title + assignee
    - Current active PR (if any): number + title + status (draft/ready/merge-ready)
    - Queue depth (number of queued issues with status:queued label)
    - Last event timestamp (human-readable: "2 minutes ago")
    - Health indicator (green/yellow/red)

Scenario: View current active issue
  Given a repository has an active issue assigned to @copilot
  When I view the dashboard
  Then the active issue is shown with:
    - Issue number + title (clickable → GitHub)
    - Assigned to: @copilot
    - Created date
    - Current labels (e.g., status:in_progress)
    - Last activity timestamp

Scenario: View current active PR
  Given a repository has a PR from the active issue
  When I view the dashboard
  Then the active PR is shown with:
    - PR number + title (clickable → GitHub)
    - Status (draft / ready_for_review / changes_requested / merge_ready)
    - CI status (passing / failing / pending) with check names
    - Latest commit message (truncated)
    - Assignee + reviewer list

Scenario: View queue of pending issues
  Given multiple issues with status:queued label exist
  When I view the dashboard
  Then I see a "Queue" section showing:
    - Number of queued issues
    - Preview of next 3-5 issues (number + title)
    - "View All" link → queue detail page (future story)

Scenario: View repository health
  Given a repository is connected
  When I view the dashboard
  Then a health indicator shows:
    - Green: All systems normal (webhooks received, no errors)
    - Yellow: Warnings (no events in last hour, API rate limit warning)
    - Red: Critical (webhook handler crashed, database unreachable)

Scenario: Navigate to repository detail
  Given I am viewing the dashboard
  When I click on a repository name or "View Detail"
  Then I am taken to the repository detail page
  And I see:
    - Full event stream (Story 4)
    - Current issue/PR details (expanded)
    - Queue (full list, when implemented)
    - Automation logs (future: actions taken by the tool)

Scenario: Dashboard auto-refresh (optional)
  Given I am viewing the dashboard
  When new webhook events are received
  Then the dashboard updates automatically (every 30 seconds via polling)
  And the refresh is smooth (no flickering or scroll jumping)
  And I can disable auto-refresh if desired (user preference)

Scenario: Empty dashboard (no repositories connected)
  Given I am logged in
  And I have not connected any repositories yet (Story 0b)
  When I visit the dashboard
  Then I see a helpful message: "No repositories connected yet"
  And I see a "Connect Repositories" button (Story 0b flow)
  And I see suggested next steps:
    1. Connect repositories
    2. Label issues with status:queued
    3. Watch the orchestrator work

Scenario: Dashboard performance
  Given I have 10 connected repositories
  When I visit the dashboard
  Then the page loads in <3 seconds
  And all repository cards render without lag
```

**Definition of Ready:**

- [x] Data model for issue/PR state is finalized (derived from events)
- [x] Dashboard layout/wireframes are approved
- [x] Performance requirements are clear (\<3 seconds load time)
- [x] Real-time update mechanism is decided (polling vs. SSE)

**Out of Scope:**

- Per-issue/PR detail pages (can be future enhancement)
- Analytics/trends (Phase 8)

**Estimated Effort:** 4-6 days (SvelteKit dashboard UI + data aggregation +
auto-refresh)

**Dependencies:** Stories 0b-4 (auth, installation, event storage, event viewer,
repo list)

______________________________________________________________________

## Story 6: CLI Commands

**User Story:**

> As a **tool operator**, I want to **manage the tool via CLI commands** (start,
> stop, restart, status), so that **I can run the tool locally and in Docker
> with confidence**.

**Acceptance Criteria:**

```gherkin
Scenario: Start the tool
  Given the tool package is installed (uv pip install copilot-orchestrator)
  When I run: copilot-orchestrator start
  Then:
    - The webhook receiver starts listening on port 8000
    - The event processor daemon starts (background worker)
    - The SvelteKit frontend starts on port 5173 (dev) or serves built assets (prod)
    - Database migrations run automatically
    - A success message is printed: "✓ Copilot Orchestrator started"
    - The tool is ready to receive webhooks

Scenario: Start with custom configuration
  Given the tool is installed
  When I run: copilot-orchestrator start --config ./config.yaml
  Then:
    - Configuration is loaded from the specified file
    - Environment variables override config file values
    - A summary of configuration is printed (secrets redacted)
    - The tool starts with the custom config

Scenario: Start in development mode
  Given I am developing the tool
  When I run: copilot-orchestrator start --dev
  Then:
    - SQLite is used (not PostgreSQL)
    - Debug logging is enabled (verbose output)
    - Hot reload is enabled for SvelteKit frontend
    - A warning is shown: "Running in dev mode (not for production)"

Scenario: Stop the tool
  Given the tool is running
  When I run: copilot-orchestrator stop
  Then:
    - The webhook receiver gracefully shuts down (no new requests accepted)
    - In-flight webhook events are completed (or queued for retry)
    - The event processor daemon stops
    - The frontend shuts down
    - Database connections are cleanly closed
    - A success message is printed: "✓ Copilot Orchestrator stopped"

Scenario: Restart the tool
  Given the tool is running
  When I run: copilot-orchestrator restart
  Then:
    - The tool is stopped (gracefully)
    - The tool is started again
    - Equivalent to: stop && start

Scenario: Check tool status
  Given the tool may or may not be running
  When I run: copilot-orchestrator status
  Then I see:
    - Running status (✓ running / ✗ stopped)
    - Webhook receiver status (listening on port 8000 / not listening)
    - Event processor status (running / stopped)
    - Frontend status (running on port 5173 / stopped)
    - Database connection status (✓ connected / ✗ error)
    - Last event received timestamp (or "no events yet")
    - Uptime (if running, e.g., "2h 34m")
    - Error messages (if any)

Scenario: Handle startup errors gracefully
  Given the database is unreachable
  When I run: copilot-orchestrator start
  Then:
    - A clear error message is printed: "✗ Database connection failed"
    - Suggested fixes are provided (e.g., "Check DATABASE_URL environment variable")
    - The tool does not hang or show stack traces (unless --debug flag)
    - Exit code is non-zero (1)

Scenario: Validate configuration before starting
  Given the configuration file has invalid values
  When I run: copilot-orchestrator start
  Then:
    - Configuration validation errors are printed (e.g., "GITHUB_APP_ID is required")
    - The tool does not start
    - A link to documentation is provided
    - Exit code is non-zero (1)

Scenario: Show help and version
  Given I want to check tool options
  When I run: copilot-orchestrator --help
  Then I see all available commands and options

  When I run: copilot-orchestrator --version
  Then I see the installed version (e.g., "0.1.0")
```

**Definition of Ready:**

- [x] Python packaging structure is designed (pyproject.toml, managed by `uv`)
- [x] CLI framework is chosen (Typer recommended, FastAPI ecosystem)
- [x] Configuration file format is designed (YAML or TOML)
- [x] Environment variable mappings are documented
- [x] Docker entrypoint script is sketched
- [x] `uv` is used for virtual environment and dependency management

**Configuration Schema (Example):**

```yaml
# config.yaml
github:
  app_id: "123456"
  private_key_path: "/secrets/github-app-key.pem"
  webhook_secret: "${GITHUB_WEBHOOK_SECRET}"
  client_id: "${GITHUB_CLIENT_ID}"
  client_secret: "${GITHUB_CLIENT_SECRET}"

server:
  port: 8000
  host: "0.0.0.0"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR

database:
  type: "postgresql"  # or "sqlite" for dev
  url: "${DATABASE_URL}"
  pool_size: 10

frontend:
  port: 5173
  build_dir: "./frontend/build"

orchestration:
  max_concurrent_issues_per_repo: 1
  event_retention_days: 365
  queue_timeout_minutes: 60

session:
  secret_key: "${SESSION_SECRET_KEY}"
  expiration_days: 30
```

**Out of Scope:**

- Interactive CLI prompts (can be future enhancement)
- Remote management (accessing tool from outside machine)

**Estimated Effort:** 2-3 days (Typer CLI + config parsing + startup/shutdown
logic)

**Dependencies:** All other Phase 1 stories must be mostly complete
(integration)

______________________________________________________________________

## Phase 1 Stories Summary

| #   | Story          | Title                          | INVEST | Dependencies  | Effort | Priority  |
| --- | -------------- | ------------------------------ | ------ | ------------- | ------ | --------- |
| 0   | Authentication | User OAuth Login               | ✅     | None          | 3-4d   | 🔴 HIGH   |
| 0b  | Installation   | App Installation & Repo Access | ✅     | Story 0       | 4-5d   | 🔴 HIGH   |
| 1   | Webhook        | GitHub App Webhook Receiver    | ✅     | Story 0b      | 3-5d   | 🔴 HIGH   |
| 2   | Storage        | Event Stream Storage           | ✅     | Story 1       | 3-5d   | 🔴 HIGH   |
| 3   | Repo UI        | Repository Selection UI        | ✅     | Stories 0b, 2 | 2-4d   | 🟡 MEDIUM |
| 4   | Event UI       | Event Stream Viewer            | ✅     | Stories 0b-3  | 4-6d   | 🟡 MEDIUM |
| 5   | Dashboard      | Minimal Dashboard              | ✅     | Stories 0b-4  | 4-6d   | 🟡 MEDIUM |
| 6   | CLI            | CLI Commands                   | ✅     | All others    | 2-3d   | 🟡 MEDIUM |

**Total Phase 1 Effort:** ~25-38 days (solo developer)

**With GitHub Copilot Coding Agent:** ~2-3 weeks (parallelizable stories)

______________________________________________________________________

## Dependency Graph

```
Story 0: Authentication (OAuth)
  ↓
Story 0b: Installation & Repo Access
  ↓
Story 1: Webhook Receiver
  ↓
Story 2: Event Storage
  ↓
Story 3: Repository UI ────┐
  ↓                         ↓
Story 4: Event Viewer       ↓
  ↓                         ↓
Story 5: Dashboard ←────────┘
  ↓
Story 6: CLI (integration)
```

______________________________________________________________________

## Implementation Order (Recommended)

1. **Week 1:** Stories 0, 0b, 1 (authentication + installation + webhooks)
1. **Week 2:** Stories 2, 3 (event storage + repo UI)
1. **Week 3:** Stories 4, 5, 6 (event viewer + dashboard + CLI)

______________________________________________________________________

## Next Steps

**Ready for @story-quality-gate validation:**

- ✅ All stories follow INVEST principles
- ✅ Acceptance criteria use Given/When/Then format
- ✅ Happy path + edge cases covered
- ✅ Definition of Ready checklists complete
- ✅ Dependencies identified
- ✅ Estimated effort provided

**Questions for validation:**

1. Are stories independent enough? (Can they be developed in parallel?)
1. Are stories small enough? (1-2 weeks per story?)
1. Are acceptance criteria testable?
1. Are edge cases comprehensive?

______________________________________________________________________

**Document generated by:** @story-builder agent

**Next agent:** @story-quality-gate (validation)

**Related documents:**

- [Feature One-Pager](copilot-workflow-orchestrator-feature-onepager.md)
- [Original Requirements](copilot-workflow-orchestrator-requirements.md)
