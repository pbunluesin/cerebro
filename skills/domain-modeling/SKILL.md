---
name: domain-modeling
description: Build and maintain a software project's precise domain language, bounded contexts, ownership, and durable architecture decisions. Use when requirements contain vague or overloaded business terms; when entities, states, identifiers, invariants, or context ownership are unclear; when code and documentation disagree about domain behavior; while grilling a new project; or before changing a domain model or recording an ADR. Keep the glossary free of implementation detail and write only confirmed knowledge.
---

# Domain Modeling

Create a shared language that users, documentation, code, and tests can use without translation.

## Operating contract

- Read the closest `AGENTS.md`, document routing, existing domain context, requirements, architecture, data docs, and accepted decisions.
- Treat code and tests as evidence of current behavior, not automatic proof of intended behavior.
- Never invent a term, invariant, context, or ownership rule. Mark proposals until the user or authoritative source confirms them.
- Challenge ambiguity when it changes behavior; do not turn ordinary technical vocabulary into domain jargon.
- Keep domain language in context documents, behavior in requirements, implementation structure in architecture, and current work in project state.
- Do not create an ADR merely to preserve conversation history.

Read [domain-modeling-standard.md](references/domain-modeling-standard.md) in full before changing domain documents.

## Model the domain

1. Locate the canonical domain documents using project routing. Cerebro uses `docs/CONTEXT.md` for project-wide language; add `docs/CONTEXT_MAP.md` plus `docs/contexts/*.md` only when multiple real bounded contexts need their own language or ownership.
2. Extract candidate actors, concepts, identifiers, lifecycle states, events, ownership, and invariants from user language and repository evidence.
3. For each material ambiguity, ask one question at a time and recommend a canonical term.
4. Stress-test the term with a concrete happy path, edge case, and conflicting usage. Check the code when it can answer a factual question.
5. Record the term only when its meaning is confirmed. Add rejected synonyms under `Avoid` so later agents do not reintroduce them.
6. Propagate a resolved rename or ownership change to affected requirements, architecture, data, API, tests, and code only within the authorized scope.

During `create-project`, maintain confirmed terms in its decision ledger before files exist, then materialize them without reinterpretation. In an existing project, update the canonical context document as each term is confirmed only when document mutation is authorized; otherwise preserve the ledger in the conversation and propose the exact change.

## Record durable decisions

Offer or create an ADR only when all three gates pass:

1. reversal would be meaningfully costly
2. the choice would be surprising or invisible to a future maintainer
3. real alternatives were considered and the reasons matter

Use the project's single decision directory, normally `docs/decisions/`. Record the smallest explanation that preserves context, choice, rationale, consequences, validation, and a revisit trigger. Do not duplicate the decision in `PROJECT_STATE.md`.

## Validate

Before reporting completion:

- search for conflicting uses of changed terms
- verify context links and decision numbering
- distinguish intended rules from merely observed implementation
- confirm every new context has explicit ownership and relationships
- report unresolved language and downstream documents not updated

Output the changed terms, evidence, contradictions resolved, ADRs created or skipped, checks run, and residual ambiguity.
