# Review / Fix Workflow

## Purpose

This document explains how code review and bug fixing work in this project.

The workflow intentionally separates reviewer and fixer roles:

```text
Claude implements → Codex reviews → Claude fixes → optional Codex re-review → Human approves
```

## Core Files

| File | Purpose |
|---|---|
| `CODE_REVIEW.md` | Single source of truth for review scope, invariants, severity, bug template, verification commands |
| `.claude/agents/codex-reviewer.md` | Claude Code subagent that orchestrates Codex review and writes review artifacts only |
| `.claude/agents/claude-fixer.md` | Claude Code subagent that fixes one OPEN bug at a time |
| `docs/bugs/*.md` | One file per confirmed bug |
| `docs/review_findings.md` | Review index and highest-priority remaining fix |

## Roles

### `codex-reviewer`

Use after non-trivial changes.

Responsibilities:

- Read `CODE_REVIEW.md`
- Run verification commands
- Ask Codex for structured findings
- Validate findings against the review brief
- De-duplicate existing bugs
- Write only review artifacts:
  - `docs/bugs/*.md`
  - `docs/review_findings.md`

Hard boundary:

- Never edits application code
- Never fixes bugs
- Never marks bugs `FIXED`

### `claude-fixer`

Use after `codex-reviewer` has filed OPEN bugs.

Responsibilities:

- Fix the highest-priority OPEN bug by default
- Reproduce the bug first
- Add/finalize a regression test or manual verification
- Implement the smallest invariant-safe fix
- Run verification commands
- Mark bug `FIXED` only when green relative to baseline

Hard boundary:

- Never calls Codex
- Never fixes multiple bugs unless explicitly requested
- Never weakens tests
- Never violates frozen decisions

## Recommended Commands in Claude Code

### Review current diff

```text
Use the codex-reviewer agent to review the current uncommitted diff in DIFF mode.
Follow CODE_REVIEW.md. Review only. Do not modify application code.
```

### Review against a branch/range

```text
Use the codex-reviewer agent to review git diff main...HEAD.
Follow CODE_REVIEW.md. Review only. Do not modify application code.
```

### Full audit

```text
Use the codex-reviewer agent in AUDIT mode for the scope defined in CODE_REVIEW.md.
Do not edit application code.
```

### Fix highest-priority bug

```text
Use the claude-fixer agent to fix the single highest-priority OPEN bug from docs/review_findings.md.
Follow CODE_REVIEW.md. Fix one bug only.
```

### Fix a specific bug

```text
Use the claude-fixer agent to fix BUG-003 only.
Follow CODE_REVIEW.md. Do not fix other bugs.
```

### Re-review after fix

```text
Use the codex-reviewer agent to re-review the fix diff for BUG-003.
Review only. Do not modify application code.
```

## Safety Rules

- `CODE_REVIEW.md` controls the review and fix loop.
- `codex-reviewer` is read/review/report only.
- `claude-fixer` is implementation/fix only.
- High-risk or low-confidence fixes should be re-reviewed.
- Human approval is required for R0/R1 changes.
