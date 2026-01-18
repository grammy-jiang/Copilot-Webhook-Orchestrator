# Phase 1 OpenAPI Contract

**Agent:** @arch-spec-author

**Date:** January 18, 2026

______________________________________________________________________

## Overview

This document defines the REST API contract for Phase 1 of the Copilot Workflow
Orchestrator. The API follows REST conventions with JSON request/response
bodies.

______________________________________________________________________

## Base URL

- **Development:** `http://localhost:8000/api`
- **Production:** `https://orchestrator.example.com/api`

______________________________________________________________________

## Authentication

All endpoints except `/health` and `/webhooks/*` require authentication via
session cookie.

| Header/Cookie             | Description                    |
| ------------------------- | ------------------------------ |
| `Cookie: session=<token>` | Session token from OAuth login |

Unauthenticated requests return `401 Unauthorized`.

______________________________________________________________________

## Error Model

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### Error Codes

| Code               | HTTP Status | Description                               |
| ------------------ | ----------- | ----------------------------------------- |
| `UNAUTHORIZED`     | 401         | Missing or invalid session                |
| `FORBIDDEN`        | 403         | User lacks permission for this resource   |
| `NOT_FOUND`        | 404         | Resource does not exist                   |
| `VALIDATION_ERROR` | 422         | Request validation failed                 |
| `CONFLICT`         | 409         | Resource already exists (e.g., duplicate) |
| `INTERNAL_ERROR`   | 500         | Unexpected server error                   |

______________________________________________________________________

## Endpoints

### Health Check

#### `GET /health`

Check service health and database connectivity.

**Authentication:** None

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "timestamp": "2026-01-18T10:30:00Z"
}
```

**Response:** `503 Service Unavailable`

```json
{
  "status": "unhealthy",
  "version": "0.1.0",
  "database": "disconnected",
  "timestamp": "2026-01-18T10:30:00Z"
}
```

______________________________________________________________________

### Authentication

#### `GET /auth/login`

Initiate GitHub OAuth flow.

**Authentication:** None

**Response:** `302 Found`

Redirects to GitHub OAuth authorization URL with:

- `client_id`
- `redirect_uri`
- `scope` (read:user, user:email)
- `state` (CSRF token)

______________________________________________________________________

#### `GET /auth/callback`

Handle GitHub OAuth callback.

**Authentication:** None

**Query Parameters:**

| Parameter | Type   | Required | Description                    |
| --------- | ------ | -------- | ------------------------------ |
| `code`    | string | Yes      | Authorization code from GitHub |
| `state`   | string | Yes      | CSRF state token               |

**Response:** `302 Found`

On success, redirects to `/dashboard` with session cookie set.

**Response:** `400 Bad Request`

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid or expired state token"
  }
}
```

______________________________________________________________________

#### `GET /auth/me`

Get current authenticated user.

**Authentication:** Required

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "github_id": 12345678,
  "username": "octocat",
  "email": "octocat@github.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
  "created_at": "2026-01-15T09:00:00Z"
}
```

______________________________________________________________________

#### `POST /auth/logout`

End current session.

**Authentication:** Required

**Response:** `200 OK`

```json
{
  "message": "Logged out successfully"
}
```

Clears session cookie.

______________________________________________________________________

### Installations

#### `GET /installations`

List user's GitHub App installations.

**Authentication:** Required

**Response:** `200 OK`

```json
{
  "installations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "installation_id": 12345,
      "account_login": "octocat",
      "account_type": "User",
      "is_suspended": false,
      "repository_count": 5,
      "created_at": "2026-01-15T09:00:00Z"
    }
  ]
}
```

______________________________________________________________________

#### `GET /installations/new`

Redirect to GitHub App installation page.

**Authentication:** Required

**Response:** `302 Found`

Redirects to `https://github.com/apps/{app-name}/installations/new`

______________________________________________________________________

#### `GET /installations/callback`

Handle GitHub App installation callback.

**Authentication:** Required

**Query Parameters:**

| Parameter         | Type    | Required | Description                      |
| ----------------- | ------- | -------- | -------------------------------- |
| `installation_id` | integer | Yes      | GitHub installation ID           |
| `setup_action`    | string  | No       | `install`, `update`, or `delete` |

**Response:** `302 Found`

Redirects to `/dashboard` after processing installation.

______________________________________________________________________

#### `GET /installations/{installation_id}`

Get installation details.

**Authentication:** Required

**Path Parameters:**

| Parameter         | Type | Description     |
| ----------------- | ---- | --------------- |
| `installation_id` | UUID | Installation ID |

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "installation_id": 12345,
  "account_login": "octocat",
  "account_type": "User",
  "permissions": {
    "issues": "write",
    "pull_requests": "write",
    "contents": "read"
  },
  "is_suspended": false,
  "created_at": "2026-01-15T09:00:00Z",
  "repositories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "full_name": "octocat/hello-world"
    }
  ]
}
```

______________________________________________________________________

### Repositories

#### `GET /repos`

List repositories accessible to the user.

**Authentication:** Required

**Query Parameters:**

| Parameter | Type    | Default | Description                    |
| --------- | ------- | ------- | ------------------------------ |
| `page`    | integer | 1       | Page number                    |
| `limit`   | integer | 20      | Items per page (max 100)       |
| `search`  | string  | -       | Filter by name (partial match) |

**Response:** `200 OK`

```json
{
  "repositories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "github_id": 123456789,
      "owner": "octocat",
      "name": "hello-world",
      "full_name": "octocat/hello-world",
      "description": "My first repository",
      "is_private": false,
      "last_event_at": "2026-01-18T10:00:00Z",
      "event_count": 42,
      "health_status": "healthy"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

### Health Status Values

| Status    | Description                              |
| --------- | ---------------------------------------- |
| `healthy` | Events received within last hour         |
| `warning` | No events in last 24 hours               |
| `error`   | Webhook errors or installation suspended |

______________________________________________________________________

#### `GET /repos/{repo_id}`

Get repository details.

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description   |
| --------- | ---- | ------------- |
| `repo_id` | UUID | Repository ID |

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "github_id": 123456789,
  "owner": "octocat",
  "name": "hello-world",
  "full_name": "octocat/hello-world",
  "description": "My first repository",
  "url": "https://github.com/octocat/hello-world",
  "is_private": false,
  "default_branch": "main",
  "last_event_at": "2026-01-18T10:00:00Z",
  "event_count": 42,
  "health_status": "healthy",
  "created_at": "2026-01-15T09:00:00Z"
}
```

______________________________________________________________________

### Events

#### `GET /repos/{repo_id}/events`

List events for a repository.

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description   |
| --------- | ---- | ------------- |
| `repo_id` | UUID | Repository ID |

**Query Parameters:**

| Parameter      | Type     | Default | Description                    |
| -------------- | -------- | ------- | ------------------------------ |
| `page`         | integer  | 1       | Page number                    |
| `limit`        | integer  | 50      | Items per page (max 100)       |
| `event_type`   | string   | -       | Filter by event type           |
| `event_action` | string   | -       | Filter by action               |
| `actor`        | string   | -       | Filter by actor username       |
| `start_date`   | datetime | -       | Filter events after this date  |
| `end_date`     | datetime | -       | Filter events before this date |

**Response:** `200 OK`

```json
{
  "events": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "delivery_id": "abc123-def456",
      "event_type": "pull_request",
      "event_action": "opened",
      "actor": "octocat",
      "target_object_ids": {
        "pr_number": 42
      },
      "received_at": "2026-01-18T10:30:00Z",
      "github_timestamp": "2026-01-18T10:29:58Z",
      "processing_status": "processed"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

______________________________________________________________________

#### `GET /repos/{repo_id}/events/{event_id}`

Get event details including raw payload.

**Authentication:** Required

**Path Parameters:**

| Parameter  | Type | Description   |
| ---------- | ---- | ------------- |
| `repo_id`  | UUID | Repository ID |
| `event_id` | UUID | Event ID      |

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "delivery_id": "abc123-def456",
  "event_type": "pull_request",
  "event_action": "opened",
  "actor": "octocat",
  "target_object_ids": {
    "pr_number": 42
  },
  "received_at": "2026-01-18T10:30:00Z",
  "github_timestamp": "2026-01-18T10:29:58Z",
  "processing_status": "processed",
  "raw_payload": {
    "action": "opened",
    "number": 42,
    "pull_request": {
      "title": "Add new feature",
      "user": { "login": "octocat" }
    }
  }
}
```

______________________________________________________________________

#### `GET /events/recent`

Get recent events across all repositories.

**Authentication:** Required

**Query Parameters:**

| Parameter | Type    | Default | Description               |
| --------- | ------- | ------- | ------------------------- |
| `limit`   | integer | 10      | Number of events (max 50) |

**Response:** `200 OK`

```json
{
  "events": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "repository": {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "full_name": "octocat/hello-world"
      },
      "event_type": "pull_request",
      "event_action": "opened",
      "actor": "octocat",
      "received_at": "2026-01-18T10:30:00Z"
    }
  ]
}
```

______________________________________________________________________

### Dashboard

#### `GET /dashboard`

Get dashboard summary across all repositories.

**Authentication:** Required

**Response:** `200 OK`

```json
{
  "summary": {
    "total_repositories": 5,
    "active_issues": 2,
    "active_prs": 3,
    "queued_issues": 7,
    "events_today": 42,
    "errors_today": 0
  },
  "repositories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "full_name": "octocat/hello-world",
      "health_status": "healthy",
      "active_issue": {
        "number": 5,
        "title": "Add new feature",
        "assignee": "copilot[bot]",
        "labels": ["status:in_progress"]
      },
      "active_pr": {
        "number": 42,
        "title": "Add new feature",
        "status": "ready_for_review",
        "ci_status": "passing"
      },
      "queue_depth": 3,
      "last_event_at": "2026-01-18T10:30:00Z"
    }
  ]
}
```

______________________________________________________________________

### Webhooks

#### `POST /webhooks/github`

Receive GitHub webhook events.

**Authentication:** None (signature verification)

**Headers:**

| Header                | Required | Description           |
| --------------------- | -------- | --------------------- |
| `X-Hub-Signature-256` | Yes      | HMAC-SHA256 signature |
| `X-GitHub-Delivery`   | Yes      | Unique delivery ID    |
| `X-GitHub-Event`      | Yes      | Event type            |
| `Content-Type`        | Yes      | `application/json`    |

**Request Body:** GitHub webhook payload (varies by event type)

**Response:** `200 OK`

```json
{
  "status": "received",
  "delivery_id": "abc123-def456"
}
```

**Response:** `202 Accepted` (for large payloads, async processing)

```json
{
  "status": "queued",
  "delivery_id": "abc123-def456"
}
```

**Response:** `401 Unauthorized` (signature verification failed)

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid webhook signature"
  }
}
```

______________________________________________________________________

## OpenAPI Specification (YAML)

```yaml
openapi: 3.1.0
info:
  title: Copilot Workflow Orchestrator API
  version: 0.1.0
  description: Webhook-driven automation service for GitHub Copilot workflow management

servers:
  - url: http://localhost:8000/api
    description: Development
  - url: https://orchestrator.example.com/api
    description: Production

paths:
  /health:
    get:
      summary: Health check
      operationId: healthCheck
      tags: [Health]
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '503':
          description: Service is unhealthy

  /auth/login:
    get:
      summary: Initiate OAuth login
      operationId: authLogin
      tags: [Authentication]
      responses:
        '302':
          description: Redirect to GitHub OAuth

  /auth/callback:
    get:
      summary: OAuth callback
      operationId: authCallback
      tags: [Authentication]
      parameters:
        - name: code
          in: query
          required: true
          schema:
            type: string
        - name: state
          in: query
          required: true
          schema:
            type: string
      responses:
        '302':
          description: Redirect to dashboard
        '400':
          description: Invalid state token

  /auth/me:
    get:
      summary: Get current user
      operationId: authMe
      tags: [Authentication]
      security:
        - sessionCookie: []
      responses:
        '200':
          description: Current user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '401':
          description: Unauthorized

  /auth/logout:
    post:
      summary: Logout
      operationId: authLogout
      tags: [Authentication]
      security:
        - sessionCookie: []
      responses:
        '200':
          description: Logged out

  /repos:
    get:
      summary: List repositories
      operationId: listRepos
      tags: [Repositories]
      security:
        - sessionCookie: []
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: List of repositories
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RepositoryList'

  /repos/{repo_id}:
    get:
      summary: Get repository
      operationId: getRepo
      tags: [Repositories]
      security:
        - sessionCookie: []
      parameters:
        - $ref: '#/components/parameters/RepoIdParam'
      responses:
        '200':
          description: Repository details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Repository'
        '404':
          description: Repository not found

  /repos/{repo_id}/events:
    get:
      summary: List events for repository
      operationId: listRepoEvents
      tags: [Events]
      security:
        - sessionCookie: []
      parameters:
        - $ref: '#/components/parameters/RepoIdParam'
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
        - name: event_type
          in: query
          schema:
            type: string
        - name: start_date
          in: query
          schema:
            type: string
            format: date-time
        - name: end_date
          in: query
          schema:
            type: string
            format: date-time
      responses:
        '200':
          description: List of events
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventList'

  /webhooks/github:
    post:
      summary: GitHub webhook receiver
      operationId: receiveWebhook
      tags: [Webhooks]
      parameters:
        - name: X-Hub-Signature-256
          in: header
          required: true
          schema:
            type: string
        - name: X-GitHub-Delivery
          in: header
          required: true
          schema:
            type: string
        - name: X-GitHub-Event
          in: header
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Event received
        '401':
          description: Invalid signature

components:
  securitySchemes:
    sessionCookie:
      type: apiKey
      in: cookie
      name: session

  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1

    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100

    RepoIdParam:
      name: repo_id
      in: path
      required: true
      schema:
        type: string
        format: uuid

  schemas:
    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, unhealthy]
        version:
          type: string
        database:
          type: string
        timestamp:
          type: string
          format: date-time

    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        github_id:
          type: integer
        username:
          type: string
        email:
          type: string
        avatar_url:
          type: string
        created_at:
          type: string
          format: date-time

    Repository:
      type: object
      properties:
        id:
          type: string
          format: uuid
        github_id:
          type: integer
        owner:
          type: string
        name:
          type: string
        full_name:
          type: string
        description:
          type: string
        is_private:
          type: boolean
        last_event_at:
          type: string
          format: date-time
        event_count:
          type: integer
        health_status:
          type: string
          enum: [healthy, warning, error]

    RepositoryList:
      type: object
      properties:
        repositories:
          type: array
          items:
            $ref: '#/components/schemas/Repository'
        pagination:
          $ref: '#/components/schemas/Pagination'

    Event:
      type: object
      properties:
        id:
          type: string
          format: uuid
        delivery_id:
          type: string
        event_type:
          type: string
        event_action:
          type: string
        actor:
          type: string
        target_object_ids:
          type: object
        received_at:
          type: string
          format: date-time
        processing_status:
          type: string
          enum: [received, processing, processed, failed]

    EventList:
      type: object
      properties:
        events:
          type: array
          items:
            $ref: '#/components/schemas/Event'
        pagination:
          $ref: '#/components/schemas/Pagination'

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        total_pages:
          type: integer

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object
```

______________________________________________________________________

**Document generated by:** @arch-spec-author agent
