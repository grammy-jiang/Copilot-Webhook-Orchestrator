# ADR-002: Synchronous Webhook Processing in Phase 1

**Status:** Accepted

**Date:** January 18, 2026

**Deciders:** @arch-spec-author, @requirements

______________________________________________________________________

## Context

GitHub sends webhook events via HTTP POST. We must decide whether to:

- Process events synchronously (in the request handler)
- Process events asynchronously (queue to a background worker)

The choice affects complexity, reliability, and latency.

______________________________________________________________________

## Decision

We will use **synchronous processing** in Phase 1, with fast acknowledgment.

The webhook handler will:

1. Verify signature immediately
1. Return `200 OK` after signature verification
1. Parse and store the event in the same request
1. Keep total response time under 500ms

______________________________________________________________________

## Options Considered

### Option A: Synchronous Processing (Selected)

**Flow:**

```
GitHub → Webhook Handler → Verify → Store → 200 OK
```

**Pros:**

- Simple architecture (no message queue)
- Fewer moving parts to deploy and monitor
- Adequate for Phase 1 volume (~30 events/min)
- FastAPI async handles concurrent requests efficiently

**Cons:**

- If storage is slow, GitHub may retry (but we return 200 early)
- No built-in retry for failed storage (rely on GitHub redelivery)
- Single point of failure (if backend is down, events are delayed)

### Option B: Asynchronous with Message Queue

**Flow:**

```
GitHub → Webhook Handler → Verify → Enqueue → 200 OK
         └──────────────────────────────────────────────┐
                                                        ▼
                              Worker → Dequeue → Store → Done
```

**Pros:**

- Decouples ingestion from processing
- Built-in retry with dead-letter queue
- Scales horizontally (add workers)
- Handles burst traffic better

**Cons:**

- Adds complexity (Redis/RabbitMQ/SQS)
- More infrastructure to deploy
- More failure modes to handle
- Overkill for Phase 1 volume

______________________________________________________________________

## Consequences

### Positive

- Faster time to MVP
- Simpler deployment (single backend service)
- Easier debugging (event stored immediately)

### Negative

- Must revisit in Phase 3+ if volume increases
- If database is slow, GitHub may timeout (mitigated by returning 200 early)

### Mitigations

- Return `200 OK` immediately after signature verification
- Use database connection pooling
- Add health monitoring for ingestion latency
- GitHub retries failed deliveries automatically

### Future Migration Path

When Phase 3+ requires higher throughput:

1. Add Redis or RabbitMQ
1. Change webhook handler to enqueue instead of store
1. Add worker service to process queue
1. Same event storage logic, different trigger

______________________________________________________________________

## Related Documents

- [Phase 1 Architecture Brief](../phase-1-architecture-brief.md)
- [Feature One-Pager](../../copilot-workflow-orchestrator-feature-onepager.md)

______________________________________________________________________

**Decision recorded by:** @arch-spec-author agent
