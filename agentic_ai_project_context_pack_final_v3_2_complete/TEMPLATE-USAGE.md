# Template Usage Guide

## Recommended usage

1. Copy `project-root/` into your real project root.
2. Replace placeholders such as `[PROJECT_NAME]`, `[STACK]`, `[DATABASE]`, `[CLOUD]`, `[OWNER]`.
3. Ask Claude Code to read `AGENTS.md`, `CLAUDE.md`, `PROCESS.md`, and `PROJECT_STATE.md`.
4. Ask Codex to review using `AGENTS.md` and the relevant docs.
5. Keep `docs/` updated as project decisions evolve.

## Core rule

Do not make `AGENTS.md` or `CLAUDE.md` too large.

Use them to route the agent to the right documentation.

Deep knowledge belongs in `docs/`.

## Recommended agent workflow

```text
Human defines goal
    ↓
Claude plans and implements
    ↓
Claude runs checks
    ↓
Codex reviews diff
    ↓
Claude fixes valid findings
    ↓
Codex re-reviews if needed
    ↓
Human approves
    ↓
Claude updates PROJECT_STATE.md and docs/
```

## Review/Fix Usage

1. Fill in `CODE_REVIEW.md` for the real project.
2. After a non-trivial Claude implementation, run `codex-reviewer`.
3. Review artifacts are written to `docs/bugs/` and `docs/review_findings.md`.
4. Run `claude-fixer` to fix one OPEN bug.
5. Re-run `codex-reviewer` for high-severity or low-confidence fixes.
