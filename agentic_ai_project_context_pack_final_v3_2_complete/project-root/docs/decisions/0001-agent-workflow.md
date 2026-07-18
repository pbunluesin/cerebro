# ADR 0001: Agentic AI Workflow

## Status

Accepted

## Context

The project may be developed with multiple AI agents. Without clear responsibility boundaries, agents may overwrite each other's intent or make changes without understanding project context.

## Decision

Use the following role separation:

- Claude Code is the main implementer and fixer.
- Codex is the independent reviewer.
- Human owner is the final decision maker.
- Gemini/ChatGPT are advisory agents.

Codex should review by default.
Claude should apply valid fixes.

## Consequences

Positive:

- Reduces single-agent bias.
- Preserves implementation context.
- Keeps review independent.

Trade-off:

- Slightly slower than letting every agent modify code directly.
- Requires maintaining `PROCESS.md` and `PROJECT_STATE.md`.
