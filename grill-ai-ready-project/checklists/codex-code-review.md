# Codex Code Review Checklist

Use after implementation, before PR merge or production deployment.

## Inputs to Codex

- `git diff` or PR diff
- changed file list
- test/build output
- relevant docs: REQUIREMENTS, ARCHITECTURE, API_SPEC, DATA_MODEL, SECURITY, TESTING
- `PLAN.md` and `PLAN-REVIEW-LOG.md` if plan review occurred

## Ask Codex to Review

- correctness against requirements
- regressions and missing edge cases
- security issues and data leaks
- auth/permission bypass
- payment/callback/reconciliation bugs
- database transaction/idempotency issues
- error handling and retry behavior
- observability/logging gaps
- tests that should be added

## Output Expected

- severity-ranked findings
- exact file/area references
- recommended fix for each finding
- final status: APPROVED | NEEDS_FIXES | BLOCKED

## Rule

Codex reviews code; Claude fixes code only after user-approved or process-approved review findings.
