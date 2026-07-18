# Code Review Standard

## Contents

1. Evidence gate
2. Review lenses
3. Severity fallback
4. Finding exclusions
5. Review completion

## Evidence gate

File a defect only when all are present:

1. Changed code or a directly affected contract.
2. A reachable input, state, timing, actor, or dependency condition.
3. An incorrect observable result or violated invariant.
4. Material user, data, security, compatibility, operational, or maintenance impact.
5. A precise location and a plausible verification method.

When execution is impractical, logical evidence may be sufficient if every step is grounded in inspected code and contracts. State the limit.

## Review lenses

### Requirement preservation

- Changed behavior maps to confirmed requirements and acceptance criteria.
- Non-goals and frozen decisions remain intact.
- Error and empty states are not silently changed.

### Control flow and state

- Branches, early returns, cleanup, cancellation, and terminal states are correct.
- Retries, replays, duplicates, and concurrent updates cannot create invalid state.
- Errors are propagated or translated at the correct boundary.

### Data integrity

- Validation occurs before irreversible effects.
- Transactions, constraints, identifiers, precision, time zones, and null semantics preserve invariants.
- Migrations are compatible, reversible or forward-recoverable, and reconciled.
- Caches and derived state cannot become authoritative accidentally.

### Security and privacy

- Authorization is checked for the actual resource and tenant.
- User-controlled input does not reach injection, traversal, SSRF, deserialization, or command boundaries unsafely.
- Secrets and sensitive values do not leak through logs, errors, telemetry, URLs, or committed files.
- Cryptographic and token/session handling follows project contracts.

### APIs and integrations

- Request/response/event schemas and error behavior remain compatible.
- Timeouts, retries, idempotency, ordering, pagination, rate limits, and signature verification are correct.
- Partial failure is visible and recoverable.
- Provider assumptions are supported by authoritative contract evidence.

### Reliability and operations

- Resource cleanup, connection lifecycle, backpressure, and bounded work are safe.
- Logs, metrics, traces, and alerts expose material success and failure.
- Rollback works with changed configuration, contracts, and data.
- Feature flags and staged rollouts have safe defaults and cleanup plans.

### Tests

- Tests prove behavior rather than implementation trivia.
- New failure and recovery paths have regression coverage.
- Mocks do not erase the contract being tested.
- Assertions would fail on the proposed defect.

### Maintainability

- New abstractions have a demonstrated variation or boundary.
- Naming and module ownership make invariants harder, not easier, to violate.
- Error handling and configuration are not duplicated inconsistently.
- Complexity added is proportional to requirements.

## Severity fallback

- `CRITICAL`: exploitable security issue, irreversible data loss, or system-wide outage likely under realistic conditions.
- `HIGH`: material production failure, authorization breach, data corruption, or broken external contract.
- `MEDIUM`: correctness or robustness failure under a realistic edge condition with contained blast radius.
- `LOW`: real, reproducible defect with minor impact; not a style preference.

Use project-defined severities when available.

## Finding exclusions

Do not file:

- stylistic preferences already handled by formatter/linter
- speculative future scale concerns outside confirmed constraints
- an issue that exists unchanged on the baseline, unless the user requested an audit
- missing tests without a corresponding unprotected behavior or regression risk
- an alternative architecture that does not correct a defect
- deliberate documented trade-offs without new contradictory evidence
- secrets themselves in review output; redact and identify the location safely

## Review completion

A review is complete when:

- every changed file was classified as reviewed or intentionally skipped
- high-risk call paths and contracts were traced beyond the diff
- relevant checks ran or their absence is disclosed
- candidates passed the evidence and baseline gates
- findings are actionable and ordered by material impact
- the reviewer did not modify the implementation
