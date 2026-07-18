# Guardrails Rule

Before and during implementation, follow `docs/guardrails.md`.

## Required Behavior

- Do not guess paths, services, endpoints, database objects, or business rules.
- Do not say done/fixed/completed without verification evidence.
- Challenge major changes before implementation.
- Flag scope drift when a small task becomes a refactor or redesign.
- Classify meaningful changes as R0, R1, or R2.
- Capture recurring mistakes in local memory or sanitized project docs.

## Completion Report Format

```text
Changed:
Checked:
Result:
Risks / skipped checks:
Docs updated:
```
