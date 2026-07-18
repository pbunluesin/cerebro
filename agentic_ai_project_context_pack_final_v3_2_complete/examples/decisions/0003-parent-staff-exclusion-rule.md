# Example ADR: Parent / Staff Exclusion Rule

This is an example only. Copy it into `project-root/docs/decisions/` only if relevant.

## Context

Some systems may contain people who are both parents and staff. Incorrect sync logic can duplicate accounts or create authorization inconsistencies.

## Decision

When a parent is also an active staff member, apply a documented exclusion or transformation rule before sending data downstream.

## Consequences

Positive:

- Prevents duplicated identity handling.
- Reduces authorization and account-mapping risk.

Trade-off:

- Requires clear ownership of identity rules.
