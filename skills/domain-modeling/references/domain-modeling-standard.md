# Domain Modeling Standard

## Contents

1. Canonical locations
2. Term eligibility
3. Domain probes
4. Context mapping
5. Decision gate
6. Change propagation

## Canonical locations

Follow existing project routing when present. Cerebro-generated projects use:

- `docs/CONTEXT.md` for project-wide language and the single-context case
- `docs/CONTEXT_MAP.md` plus `docs/contexts/<context>.md` only when multiple bounded contexts need their own language or ownership
- `docs/decisions/NNNN-<slug>.md` for durable decisions

Create a context map lazily. Multiple deployables, folders, teams, or database schemas do not by themselves prove multiple bounded contexts.

## Term eligibility

A context term must be specific to how this domain speaks or reasons. Include:

- canonical term
- one- or two-sentence definition
- rejected or ambiguous synonyms under `Avoid`
- link to another context when the same word has a different meaning there

Exclude framework vocabulary, implementation classes, generic programming concepts, temporary task names, and requirements prose.

Use this shape:

```markdown
### Canonical term

Definition: precise domain meaning.

Avoid: ambiguous synonym, implementation label
```

## Domain probes

Use only relevant probes and ask one decision at a time:

1. Identity: what makes two instances the same thing?
2. Ownership: which context may create or change it?
3. Lifecycle: which states and transitions are valid?
4. Invariant: what must remain true after every operation?
5. Time: when does it become active, expire, or become historical?
6. Quantity: what unit, rounding, limit, or precision applies?
7. Failure: what does rejection, cancellation, retry, or partial completion mean?
8. Context collision: does another part of the system use this word differently?
9. Authority: is user intent or current code the source of truth when they disagree?

Concrete scenarios are probes, not facts. Label invented examples until the user confirms their rule.

## Context mapping

Use a context map only when language or ownership truly changes across contexts. Record:

| Context | Owns | Does not own | Upstream/downstream relationship |
|---|---|---|---|
| Example | Confirmed concepts | Explicit exclusions | Contract or event relationship |

Each context document keeps its own language. `docs/CONTEXT.md` then contains only terms that genuinely apply across the project, not copied definitions from every context. Shared identifiers or values need an explicit owner or compatibility contract; do not create a vague “shared” context by default.

## Decision gate

An ADR needs all three:

- costly reversal
- surprising or invisible rationale
- genuine alternatives and trade-offs

If the gate fails, keep the fact in its canonical document or omit it. If it passes, record a compact core: status/date, context, decision, rationale, consequences, validation, and revisit trigger. Add option tables only when future readers need them.

## Change propagation

Before renaming or moving a concept, search all project artifacts. Update only authorized destinations, but report every affected surface:

- requirements and acceptance criteria
- architecture and context ownership
- data schemas and identifiers
- API/event contracts
- tests, fixtures, telemetry, and user-facing language
- code symbols when implementation is authorized

Do not mark a domain change complete while known conflicting terminology remains unexplained.
