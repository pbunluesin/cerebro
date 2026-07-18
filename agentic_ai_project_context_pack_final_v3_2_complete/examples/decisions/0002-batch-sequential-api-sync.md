# Example ADR: Use Sequential Batch API Sync

This is an example only. Copy it into `project-root/docs/decisions/` only if relevant.

## Context

Parallel vendor API sync can create rate limits, ordering issues, duplicated requests, or difficult debugging.

## Decision

Use sequential batch sync by default unless measured performance requirements justify concurrency.

## Consequences

Positive:

- Easier troubleshooting.
- Safer for vendor endpoints.

Trade-off:

- Slower than parallel execution.
