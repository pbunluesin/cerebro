# CODEX-REVIEWER.md

## Meaning

Human-readable entry point for the Codex review workflow.

The actual Claude Code subagent file is:

```text
.claude/agents/codex-reviewer.md
```

Use this root file as a visible pointer for humans, GitHub readers, and AI agents that inspect the repository root first.

## Role

Codex reviewer is the independent review pass.

- Claude orchestrates the review and collects evidence.
- Codex is used as the review brain.
- The reviewer must follow `CODE_REVIEW.md`.
- The reviewer writes only review artifacts.
- The reviewer must not edit application code.
- The reviewer must not fix bugs.

## How to invoke in Claude Code

```text
Use the codex-reviewer agent to review the current uncommitted diff in DIFF mode.
Follow CODE_REVIEW.md.
Review only.
Do not modify application code.
```

## Real source

For full implementation details, read:

```text
.claude/agents/codex-reviewer.md
```
