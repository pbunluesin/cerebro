# CLAUDE-FIXER.md

## Meaning

Human-readable entry point for the Claude fixer workflow.

The actual Claude Code subagent file is:

```text
.claude/agents/claude-fixer.md
```

Use this root file as a visible pointer for humans, GitHub readers, and AI agents that inspect the repository root first.

## Role

Claude fixer is the fix pass for OPEN bugs created by `codex-reviewer`.

- Claude is the sole author of fixes.
- Claude must follow `CODE_REVIEW.md`.
- Claude fixes one bug per run by default.
- Claude must reproduce the bug before fixing.
- Claude must add regression/manual verification.
- Claude must not call Codex during fixing.

## How to invoke in Claude Code

```text
Use the claude-fixer agent to fix the single highest-priority OPEN bug from docs/review_findings.md.
Follow CODE_REVIEW.md.
Fix one bug only.
```

## Real source

For full implementation details, read:

```text
.claude/agents/claude-fixer.md
```
