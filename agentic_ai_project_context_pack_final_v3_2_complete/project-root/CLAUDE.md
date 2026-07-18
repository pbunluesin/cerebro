# CLAUDE.md

Persistent instructions for Claude Code.

## Role

Claude Code is the main implementer and primary fixer for this project.

Claude should:

- Preserve existing architecture unless explicitly asked to redesign.
- Read `PROJECT_STATE.md` before starting.
- Read `PROCESS.md` before implementation.
- Read relevant docs under `docs/` based on task type.
- Apply fixes based on valid Codex review findings.
- Update `PROJECT_STATE.md` after completing meaningful work.
- Update `docs/` when contracts, architecture, database logic, security behavior, deployment, or business rules change.

## Implementation Rules

- Prefer small, reviewable changes.
- Do not silently change API contracts.
- Do not silently change database semantics.
- Do not modify authentication, payment, or security-sensitive logic without reading `docs/security.md`.
- Keep business rules explicit and documented.
- When unsure, produce a short implementation plan before changing code.

## Fixing Codex Review Findings

When Codex provides findings:

1. Classify each finding as valid, invalid, or needs human decision.
2. Apply fixes only for valid findings.
3. Explain rejected findings briefly.
4. Re-run relevant checks.
5. Update `PROJECT_STATE.md`.
6. Update docs if behavior changed.

## Completion Rule

A task is not complete until:

- Relevant checks were run or skipped with reason.
- Critical/high review findings are resolved.
- `PROJECT_STATE.md` is updated.
- Relevant docs are updated when behavior changed.

## Review / Fix Layer

For code review and fixes:

- Use `codex-reviewer` after non-trivial implementation.
- Use `claude-fixer` only after `codex-reviewer` has filed OPEN bugs.
- `codex-reviewer` must not edit application code.
- `claude-fixer` must not call Codex.
- `claude-fixer` fixes one bug per run by default.
- All review/fix behavior must follow `CODE_REVIEW.md`.

## Operating Guardrails

Follow `docs/guardrails.md`.

A valid completion report must include:

```text
Changed:
Checked:
Result:
Risks / skipped checks:
Docs updated:
```
