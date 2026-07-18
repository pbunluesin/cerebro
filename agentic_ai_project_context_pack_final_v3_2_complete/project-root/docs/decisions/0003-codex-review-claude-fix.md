# ADR 0003: Codex Review / Claude Fix Layer

## Status

Accepted

## Context

The project uses Claude Code as the main implementer and OpenAI Codex as an independent reviewer. The goal is to reduce single-agent bias while keeping code changes owned by the agent that has the strongest project implementation context.

## Decision

Add a formal review/fix layer:

- `CODE_REVIEW.md` defines review scope, frozen decisions, invariants, verification commands, severity, and report format.
- `.claude/agents/codex-reviewer.md` orchestrates Codex review and writes only review artifacts.
- `.claude/agents/claude-fixer.md` fixes one OPEN bug at a time and never calls Codex.
- `docs/bugs/*.md` stores one confirmed bug per file.
- `docs/review_findings.md` indexes findings and priority.
- `docs/review-workflow.md` explains how to invoke the process.

## Consequences

Positive:

- Strong separation of reviewer and fixer.
- Codex remains an independent second opinion.
- Claude remains the implementation owner.
- Bug findings become durable artifacts instead of chat-only feedback.
- Fixes require reproduction, regression test/manual verification, and baseline comparison.

Trade-off:

- More process than ad-hoc review.
- Requires `CODE_REVIEW.md` to be filled in for each real project.
- Requires Codex MCP configuration for `codex-reviewer`.
