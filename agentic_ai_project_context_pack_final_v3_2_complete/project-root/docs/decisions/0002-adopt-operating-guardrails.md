# ADR 0002: Adopt AI Operating Guardrails

## Status

Accepted

## Context

AI agents can fail in predictable ways:

- Guessing missing context
- Claiming work is complete without verification
- Expanding scope beyond the requested task
- Making high-risk changes without classifying reversibility
- Repeating the same mistakes across sessions

## Decision

Adopt AI operating guardrails:

- NO MAGIC
- VERIFY BEFORE DONE
- DISSENT
- SCOPE DRIFT
- R0/R1/R2 reversibility classification
- Local Learning Capture

These rules are documented in `docs/guardrails.md` and referenced from `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/guardrails.md`.

## Consequences

Positive:

- Reduces hallucinated paths, services, and assumptions.
- Improves completion quality by requiring evidence.
- Reduces unsafe scope creep.
- Creates a safer decision boundary for high-risk changes.
- Captures recurring mistakes as reusable lessons.

Trade-off:

- Adds a small amount of process overhead.
- Requires discipline to keep local memory sanitized and out of Git when sensitive.
