# Plan Review Standard

## Contents

1. Review order
2. Required challenges
3. High-risk lenses
4. False positives
5. Approval gate

## Review order

Review in this order so architectural flaws are not hidden by detailed steps:

1. Requirement and scope fidelity
2. System boundary and ownership
3. Trust, authorization, and sensitive data
4. Data integrity and external contracts
5. Failure, concurrency, retry, and recovery
6. Delivery, migration, rollback, and observability
7. Testability and acceptance evidence
8. Complexity, sequencing, and maintainability

## Required challenges

### Requirement fidelity

- Does every step implement a confirmed requirement?
- Does the plan introduce unrequested behavior, users, dependencies, or scope?
- Are non-goals preserved?
- Are acceptance criteria observable after implementation?

### Boundary and ownership

- Is each responsibility assigned to the correct module or service?
- Are sources of truth explicit?
- Are external systems isolated behind owned contracts?
- Does the plan create circular or hidden ownership?

### Security and privacy

- Are authentication and authorization checked at the correct boundary?
- Can one role or tenant access another's data or actions?
- Are secrets, PII, logs, and error payloads handled safely?
- Does the plan create a new trust boundary without threat analysis?

### Data and consistency

- Are identifiers, uniqueness, constraints, transaction boundaries, and reconciliation defined?
- Can retries or concurrent workers duplicate effects?
- Can partial failure leave an impossible or misleading state?
- Are migrations backward compatible and observable?

### Contracts and integrations

- Are request, response, event, webhook, timeout, retry, version, and error behaviors explicit?
- Is idempotency owned by the correct side?
- What happens when the provider is slow, unavailable, duplicated, reordered, or incompatible?
- Is a mocked assumption being mistaken for a real contract?

### Delivery and recovery

- Can the change be deployed incrementally?
- What is the point of no return?
- Is rollback compatible with changed data and contracts?
- Are feature flags, dual reads/writes, backfills, and cleanup sequenced safely when used?
- Will operators know whether deployment succeeded?

### Verification

- Does each material requirement have automated or manual evidence?
- Are tests placed at the right boundary rather than overfitting internals?
- Are failure and recovery paths covered?
- Are pre-existing failures distinguished from regressions?

### Complexity

- Is there a smaller vertical slice that delivers the confirmed outcome?
- Does abstraction precede demonstrated variation?
- Does the plan replace dependencies or refactor unrelated areas without need?
- Are irreversible choices delayed until evidence justifies them?

## High-risk lenses

### Authentication and authorization

Require explicit actors, identity provider/source, session/token lifecycle, permission checks, tenant boundary, privileged operations, revocation, audit, and recovery.

### Payments and entitlements

Require idempotency keys, immutable event history, authoritative balance/entitlement source, webhook verification, replay handling, reconciliation, refunds/reversals, and operator visibility.

### Migration and backfill

Require dry run, checkpointing, idempotency, compatibility window, reconciliation, cutover, rollback/forward recovery, and retained evidence.

### Concurrency and asynchronous work

Require ordering assumptions, locking/versioning, retry budget, deduplication, poison-message behavior, cancellation, visibility timeout, and terminal-state ownership.

### Production infrastructure

Require least privilege, environment separation, secret provisioning, plan/apply review, blast-radius limits, observability, rollback, and explicit approval for destructive actions.

## False positives

Do not flag:

- a deliberate decision documented with an accepted trade-off unless new evidence invalidates it
- missing implementation detail that the plan safely defers to a reversible coding choice
- style or technology preference without requirement impact
- hypothetical scale beyond confirmed constraints
- pre-existing architecture debt unrelated to the plan, except as a clearly separated risk

## Approval gate

Approve only when:

- confirmed scope and non-goals are preserved
- every material step has a reason and validation
- critical trust/data/contract boundaries are explicit
- realistic failure and recovery paths are addressed
- rollout and rollback are coherent with data changes
- no R0 action is hidden inside routine implementation
- residual risks are visible to the user or owner
