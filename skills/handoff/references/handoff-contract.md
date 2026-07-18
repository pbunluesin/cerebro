# Handoff Contract

## Contents

1. Same-project state
2. Cross-project dispatch
3. Delivery and discovery
4. Contract verification
5. Redaction and lifecycle

## Same-project state

`PROJECT_STATE.md` should answer:

- What outcome is currently being pursued?
- Which exact step is in progress?
- What evidence is already verified?
- What remains blocked or risky?
- Which files and contracts matter next?
- Which verified attempt must not be repeated, and what evidence rejected it?
- Which transient services, processes, or safe environment facts are required to continue?
- Which commands continue and verify the work?
- Which explicit skill or workflow should run next?
- What is the next safe, bounded action?

It should not duplicate:

- completed commit history
- full diffs or test logs
- requirement or plan text
- accepted ADR content
- review finding bodies
- generic project instructions

Link to those sources instead.

Keep the continuation block compact:

```markdown
## Handoff

- Exact stopping point: <specific step and location>
- Verified evidence: <test, command, file, or NOT VERIFIED>
- Read first: <inspected canonical files>
- Relevant contracts: <identifiers and owning files, or None>
- Do not touch: <bounded exclusions, or None>
- Do not retry: <verified dead end + evidence + revisit condition, or None>
- Runtime/environment state: <safe transient state and variable names, or None>
- Known gotchas: <non-obvious current constraint, or None>
- Next invocation: <explicit skill/workflow, or None>
- Next command: `<exact safe continuation command>`
- Verify with: `Validation commands` section
- Expected outcome: <measurable next checkpoint>
```

Do not add a rejected approach merely because another option was preferred. Record it only when an inspected artifact or reproduced attempt proves that repeating it would waste work or cause harm. Move durable architecture choices and rejected alternatives to the owning plan or ADR.

Runtime/environment state may name a local service, process, port, safe feature flag, or required variable name. Never record a secret value, copied production payload, or a machine-specific absolute path that the next controlled environment cannot use.

## Cross-project dispatch

Use this entry format:

```markdown
# Dispatch: <target>

- From: <source>
- Date: <YYYY-MM-DD>
- Status: ACTIVE

## Change

- <delta only>

## Required action

1. <specific target action>

## Breaking changes

- None | <explicit break>

## Contract

| Type | Identifier | Declared behavior | Evidence/source |
|---|---|---|---|
| HTTP/Event/Data/File | TBD | TBD | TBD |

## Verification

- TBD
```

When completed, change status to `DONE (<date>)` and add a verified commit or `No Git`. Never delete active entries.

## Delivery and discovery

The source repository owns the canonical dispatch:

```text
<source-root>/.cerebro/handoffs/<source>--<target>.md
```

Use one of these delivery paths:

1. **Shared Git path:** report the source repository, relative dispatch path, and verified commit. The target reads that exact artifact.
2. **Authorized local target:** after explicit approval for the exact target root, create `<target-root>/.cerebro/inbox/<source>--<target>.md` containing only a pointer:

```markdown
# Cerebro Dispatch Pointer

- Source repository: <remote identifier or controlled local source>
- Source dispatch: `.cerebro/handoffs/<source>--<target>.md`
- Source ref: <verified commit or No Git>
- Target: <target>
- Delivered: <YYYY-MM-DD>
```

The pointer is not a second contract and must not copy action items or status. Resolve it to the source before acting. If the source cannot be read, report `NOT VERIFIED` rather than relying on a stale copy.

Do not write to a target repository, home directory, or global inbox without explicit authorization for that exact location. Do not search sibling repositories or broad filesystem roots to discover dispatches. `check` reads only the current project's `.cerebro/inbox/`, its own `.cerebro/handoffs/`, and explicit user-supplied paths.

## Contract verification

Verify only contracts declared in the dispatch and directly related authoritative definitions:

- HTTP: method, path, auth, request, response, errors, version
- Event/webhook: name, producer, consumer, schema, signature, ordering, retry, idempotency
- Queue/job: payload, ownership, visibility/lease, retry, terminal states
- Database: object, parameters/columns, types, constraints, transaction ownership, result shape
- SQL Server stored procedure: schema-qualified name; parameter name, order, SQL type, length/precision/scale, direction, default, and nullability; table-valued parameter type; result-set count, column order/names/types/nullability; return code and output parameters; error/`THROW` behavior; transaction ownership, isolation, and `XACT_ABORT`; permissions; idempotency/concurrency expectations; deployment version
- File/export: naming, encoding, schema, partitioning, delivery, replay
- Sync: source of truth, mapping, checkpoint, conflict and reconciliation

Report:

```text
MATCH: declaration and authoritative definition agree
DRIFT: both exist but disagree
MISSING: declared item has no located implementation
UNDOCUMENTED: related implementation exists but dispatch omits it
NOT VERIFIED: authoritative source is inaccessible or ambiguous
```

Every result needs a file/line or authoritative contract reference.

## Redaction and lifecycle

- Never include passwords, tokens, connection strings, private keys, production payloads, or PII.
- Replace sensitive values with categories, not partial secret fragments.
- Keep dispatches status-based so work is not lost outside Git.
- Archive/delete only `DONE` entries and only when the user requests cleanup.
- Do not store machine-specific absolute paths unless both sides explicitly require and control the same environment.
- Do not copy an entire `PROJECT_STATE.md`, plan, diff, issue, or review report into a dispatch.
