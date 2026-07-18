# Grilling Question Bank

Use these questions selectively. Ask one question at a time.

## Goal

- What is the main outcome this project/change must achieve?
- What problem does this solve that is painful today?
- What would make this project clearly successful?

## Users / Stakeholders

- Who uses this directly?
- Who depends on its output indirectly?
- Who approves the requirement or contract?

## Scope

- What must be included in the first version?
- What is explicitly out of scope?
- What can be deferred safely?

## Data

- What is the source of truth?
- Which data can be stale, and for how long?
- What are the unique identifiers and matching keys?
- What happens with duplicates or missing values?

## API / Integration

- Who owns the request/response contract?
- What authentication is required?
- What happens on timeout, retry, duplicate request, or partial failure?
- Is the operation idempotent?

## Security

- What data is sensitive?
- Who is allowed to access or change it?
- What should never be logged?

## Testing

- How will we know it works?
- What are the critical regression flows?
- What test data is safe to use?

## Deployment

- Where will this run?
- How do we rollback?
- What must be verified after deployment?

## Recommended Answer Pattern

When asking, include a default when possible:

> My recommended default is X because Y. Is that correct, or should we use a different rule?
