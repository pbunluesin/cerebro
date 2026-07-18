# Handoff Contract

## Contents

1. Same-project state
2. Cross-project dispatch
3. Contract verification
4. Redaction and lifecycle

## Same-project state

`PROJECT_STATE.md` should answer:

- What outcome is currently being pursued?
- Which exact step is in progress?
- What evidence is already verified?
- What remains blocked or risky?
- Which files and contracts matter next?
- Which commands continue and verify the work?
- What is the next safe, bounded action?

It should not duplicate:

- completed commit history
- full diffs or test logs
- requirement or plan text
- accepted ADR content
- review finding bodies
- generic project instructions

Link to those sources instead.

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

## Contract verification

Verify only contracts declared in the dispatch and directly related authoritative definitions:

- HTTP: method, path, auth, request, response, errors, version
- Event/webhook: name, producer, consumer, schema, signature, ordering, retry, idempotency
- Queue/job: payload, ownership, visibility/lease, retry, terminal states
- Database: object, parameters/columns, types, constraints, result shape
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
