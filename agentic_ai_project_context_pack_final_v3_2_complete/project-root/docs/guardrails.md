# AI Operating Guardrails

## Purpose

This document defines behavioral guardrails for AI agents working on this project.

These rules reduce common agent failures:

- Guessing non-existent paths, services, files, or business rules
- Claiming work is complete without evidence
- Expanding scope beyond the requested task
- Making high-risk changes without identifying reversibility
- Forgetting lessons learned across sessions

## Guardrail 1: NO MAGIC — Do Not Guess

AI agents must not invent:

- File paths
- API endpoints
- Environment variables
- Database objects
- Business rules
- Service names
- Deployment environments
- External system behavior

If context is missing, the agent must either inspect the repository or explicitly state the assumption.

## Guardrail 2: VERIFY BEFORE DONE — Evidence Before Completion

AI agents must not say `done`, `fixed`, `completed`, `verified`, or `working` unless there is evidence.

A valid completion report must include:

1. What changed
2. What was checked
3. Evidence/result
4. Remaining risks or skipped checks
5. Documentation/state updates

## Guardrail 3: DISSENT — Challenge Major Changes First

Before any major change, identify:

- Blast radius
- Assumptions
- Reversibility
- Rollback strategy
- Safer alternatives

Major changes include database schema changes, stored procedure changes, API contract changes, authentication/authorization changes, payment/SSO/webhook changes, deployment pipeline changes, and vendor integration changes.

## Guardrail 4: SCOPE DRIFT — Stay Within the Task

If a small request expands into large refactor, redesign, dependency replacement, unrelated cleanup, multi-module rewrite, or architecture change, stop and flag scope drift.

## Guardrail 5: R0 / R1 / R2 — Reversibility Classification

| Level | Meaning | Examples | Required Action |
|---|---|---|---|
| R0 | Irreversible or high-risk | destructive production DB operation, payment/auth behavior, data migration with side effects | Stop and ask for approval |
| R1 | Costly to reverse | API contract change, schema change, dependency replacement, vendor integration behavior | Explain plan, risk, and rollback before proceeding |
| R2 | Easy to reverse | typo, small UI change, local refactor, test-only change | Proceed and report clearly |

## Guardrail 6: Local Learning Capture

When an agent makes a recurring mistake or an operational failure is discovered, capture the lesson.

Use this schema:

```md
## YYYY-MM-DD — [Short title]

- what happened:
- root cause:
- correct behavior next time:
```

Do not store secrets, credentials, personal data, sensitive vendor information, or production incident details in committed memory.

Recommended locations:

| Memory Type | Location | Commit? |
|---|---|---|
| Personal/local lessons | `.claude/MEMORY.local.md` | No |
| Sanitized project lesson | `docs/troubleshooting.md` or `docs/decisions/` | Yes, if useful |
| Current project state | `PROJECT_STATE.md` | Yes |
| Architecture/business rules | `docs/` | Yes |
