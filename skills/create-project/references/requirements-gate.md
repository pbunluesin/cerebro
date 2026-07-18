# Requirements Gate

## Contents

1. Gate states
2. Question routing
3. Required decision domains
4. Scenario probes
5. Readiness evaluation
6. Final requirement format

## Gate states

Use these states in order:

| State | Exit condition |
|---|---|
| `DISCOVERY` | Evidence sources inspected; contradictions and unknowns listed |
| `REQUIREMENTS_READY` | Product behavior and acceptance boundaries contain no blocking gap |
| `ARCHITECTURE_READY` | System boundaries, data ownership, trust boundaries, validation, and recovery are defined proportionally to risk |
| `IMPLEMENTATION_READY` | Project files validate and the first vertical slice has a measurable definition of done |

A user may revise an earlier decision at any time. Re-open every downstream decision affected by that revision.

## Question routing

Do not ask every question mechanically. Prioritize in this order:

1. Decisions that change the product boundary.
2. Decisions that determine trust, money, identity, or data ownership.
3. Decisions with many downstream dependencies.
4. Decisions that are costly to reverse.
5. Decisions needed to write observable acceptance criteria.
6. Implementation preferences that cannot be deferred safely.

Skip a question when reliable evidence already answers it. Cite that evidence in the ledger.

## Required decision domains

### Outcome and users

- What outcome must change, for whom, and how will success be observed?
- Who owns product decisions and who operates the system?
- What happens if the project is not built?

Block readiness when the project has no identifiable user, outcome, or success signal.

### Scope and lifecycle

- What is explicitly in scope for the first usable release?
- What is explicitly excluded?
- Is this a prototype, internal utility, maintained product, or production service?
- What compatibility, migration, or deprecation obligations exist?

Block readiness when two plausible scope interpretations would lead to materially different systems.

### Behavior and journeys

- What are the primary user journeys?
- What are the preconditions, trigger, expected result, and observable failure for each?
- What can be retried, cancelled, reversed, or resumed?
- What must be idempotent?

Block readiness when core behavior cannot be expressed as testable examples.

### Domain language and rules

- Which terms have project-specific meanings?
- Which terms are overloaded, rejected synonyms, or mean different things in different contexts?
- Which bounded context owns each important concept, and which relationships cross contexts?
- Which actor can perform which action under which conditions?
- Which invariants must always hold?
- Which calculations, time boundaries, states, or precedence rules affect behavior?

Block readiness when an overloaded term changes a business rule or data model.
Do not infer a bounded context from a folder, service, team, or database alone; require a real language or ownership boundary.

### Data

- What data enters, leaves, or persists?
- Which system is authoritative for each important datum?
- What identifiers, uniqueness rules, retention periods, deletion rules, and audit requirements apply?
- Is backfill, reconciliation, import, export, or migration needed?

Block readiness for destructive or externally synchronized data until ownership, replay, failure recovery, and rollback are defined.

### Interfaces and integrations

- Which APIs, events, webhooks, files, queues, or vendor systems participate?
- Who owns each contract and how is it versioned?
- What are timeout, retry, rate-limit, ordering, duplication, and partial-failure semantics?
- How are credentials and secrets provisioned?

Block readiness when a required external contract is unknown and cannot be safely isolated behind an adapter.

### Identity, security, privacy, and compliance

- Who authenticates users or services?
- Which roles, permissions, tenant boundaries, and privileged actions exist?
- What sensitive data is processed and where may it flow?
- What threat, abuse, logging, encryption, consent, or regulatory constraints apply?

Block readiness for auth, payment, PII, regulated, or multi-tenant work until trust boundaries and authorization behavior are explicit.

### Quality attributes

- What latency, throughput, concurrency, availability, durability, accessibility, localization, or device support is required?
- Which values are hard requirements versus goals?
- What scale is expected now and what change would invalidate the design?

Do not invent numeric targets. Recommend measurable defaults and ask when a value changes architecture or cost.

### Delivery and operations

- Which environments exist and who can deploy?
- What configuration is environment-specific?
- What must be observable through logs, metrics, traces, alerts, or audit events?
- How is deployment verified, rolled back, or recovered?
- Who responds when the system fails?

Block critical-project readiness without a rollback/recovery path and post-deployment verification.

### Verification and acceptance

- How will each requirement be verified: automated test, contract test, manual check, inspection, or production signal?
- What test data and external dependencies are required?
- Which regressions would be unacceptable?
- What evidence closes the project or release?

Block readiness when core acceptance criteria are subjective or have no verification method.

## Scenario probes

For every core journey, probe:

1. Happy path: expected input and result.
2. Invalid input: validation and user-visible response.
3. Unauthorized actor: denial behavior and audit evidence.
4. Duplicate or replay: idempotency and conflict behavior.
5. Partial failure: persisted state and retry behavior.
6. Dependency timeout: fallback, retry, and user experience.
7. Concurrency: competing updates and consistency rule.
8. Cancellation or rollback: what is reversible and by whom.
9. Boundary: empty, maximum, expired, cross-tenant, or time-zone edge.
10. Recovery: resumption after agent, process, network, or deployment interruption.

Use only relevant probes. Critical workflows normally require all ten.

## Readiness evaluation

Classify every gap:

- `BLOCKING`: a reasonable implementation choice could violate product behavior, security, data integrity, compliance, or operational safety.
- `NONBLOCKING`: a safe default exists, is reversible, and can be recorded with an owner or decision point.
- `DEFERRED`: intentionally excluded from the confirmed release scope.

Readiness requires zero `BLOCKING` gaps. It does not require pretending every future decision is known.

Reject these false signals:

- a long document with no testable acceptance criteria
- a complete-looking template still containing generic boilerplate
- a technology stack chosen before product constraints
- “secure,” “fast,” or “scalable” without observable meaning
- a happy-path-only specification
- unresolved external contracts hidden behind `TBD`

## Final requirement format

Use stable identifiers:

```text
FR-001  Functional behavior
NFR-001 Quality or operational constraint
BR-001  Business invariant
AC-001  Observable acceptance criterion
RISK-001 Material risk and mitigation
ASM-001  Explicit safe assumption
```

Each `FR`, `NFR`, and critical `BR` must map to at least one `AC`. Each acceptance criterion must name a verification method. Keep rejected and deferred scope visible so later agents do not silently reintroduce it.
