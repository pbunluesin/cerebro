# Codex Plan Review Checklist

Use before implementation for high-risk work.

## Preconditions

- `PLAN.md` exists and has a clear goal, approach, scope, risks, validation plan, and rollback notes.
- Requirement docs are available or intentionally marked TBD.
- Codex review mode is selected: MCP-first, Codex CLI, or manual prompt.
- Codex is read-only and cannot modify files.

## Review Questions

Ask Codex to look for:

- wrong or missing requirements
- unsafe assumptions
- security/auth/PII gaps
- payment/callback/webhook idempotency gaps
- reconciliation and retry gaps
- schema/data ownership conflicts
- race conditions and concurrency issues
- missing audit logs or observability
- deployment, rollback, and migration risks
- simpler safer alternatives

## Verdict Contract

Codex must end with exactly one of:

```txt
VERDICT: APPROVED
VERDICT: REVISE
```

## Claude Responsibilities

- Accept good critiques and revise the plan.
- Reject weak critiques with a logged reason.
- Append all rounds to `PLAN-REVIEW-LOG.md`.
- Stop at `MAX_ROUNDS`.
- Ask the user before code is written.
