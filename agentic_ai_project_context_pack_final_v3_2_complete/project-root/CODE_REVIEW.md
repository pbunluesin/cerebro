# CODE_REVIEW.md — Review Brief

This file drives every code-review pass.

It is the single source of truth for:

- `codex-reviewer` review behavior
- `claude-fixer` fix behavior
- bug file format
- verification commands
- frozen decisions
- domain invariants
- out-of-scope rules

Do not run a generic review. Review against this brief.

## §0 — Review Workflow

Default workflow:

```text
Claude implements → codex-reviewer reviews → docs/bugs/BUG-NNN files are created → claude-fixer fixes one OPEN bug → optional codex-reviewer re-review
```

Role split:

| Role | Owner | Rule |
|---|---|---|
| Implementation | Claude | Main author of code changes |
| Review | Codex via `codex-reviewer` | Review only; no application code edits |
| Fix | Claude via `claude-fixer` | Fix one bug at a time; never call Codex |
| Approval | Human | Final decision for R0/R1 or sensitive changes |

## §1 — Read First

Before review or fix, read:

- `AGENTS.md`
- `CLAUDE.md`
- `PROCESS.md`
- `PROJECT_STATE.md`
- `docs/README.md`
- `docs/guardrails.md`
- Relevant files under `docs/` based on the task type

Task-specific docs:

| Task | Required docs |
|---|---|
| API / integration | `docs/api-contract.md`, `docs/integration-rules.md` |
| Database / SQL | `docs/database-objects.md`, `docs/data-flow.md` |
| Auth / security / payment / SSO | `docs/security.md` |
| Deployment | `docs/deployment-runbook.md` |
| Tests | `docs/testing-strategy.md` |
| Logs / dashboards / alerts | `docs/observability.md` |

If a referenced file is missing, report it as a blocker unless explicitly optional.

## §2 — Scope

Default review mode is DIFF mode.

Review only:

- current uncommitted diff, or
- caller-provided git range/base, or
- caller-named files/feature branch

AUDIT mode is allowed only when explicitly requested.

## §3 — Frozen / Do-NOT-Flag Decisions

These are deliberate decisions. Do not flag them as bugs.

Add project-specific frozen decisions here.

Examples:

- [F-001] [Decision and reason]
- [F-002] [Decision and reason]

If a frozen decision appears harmful, report it as `DESIGN-QUESTION`, not `BUG`.

## §4 — Domain Invariants

Add project-specific invariants here.

Examples:

- [INV-001] API request/response contract must remain backward compatible unless explicitly approved.
- [INV-002] Database output shape must not change without updating docs and downstream consumers.
- [INV-003] Auth, payment, SSO, and webhook changes require explicit human approval.
- [INV-004] No production data mutation without documented rollback or recovery plan.

Every `BUG` must identify the invariant, requirement, or expected behavior it violates.

## §5 — Priority Hunt List

Use this list to focus review attention.

Examples:

1. Security and secrets
2. API contract compatibility
3. Database/data integrity
4. Auth/payment/SSO/webhook behavior
5. Edge cases and regressions
6. Test coverage gaps
7. Observability and operational failure modes

## §6 — Out of Scope

Do not flag or fix these unless explicitly requested:

- Style-only changes
- Formatting-only changes
- Import ordering
- Rename-only suggestions
- Broad refactors
- Dependency replacement
- Architecture redesign
- Unrelated cleanup

## §7 — Verification Commands

Fill in exact commands for this project.

Do not invent weaker commands during review/fix.

```bash
# Example placeholders; replace for the real project
# npm test
# npm run lint
# python -m pytest
# php -l path/to/file.php
```

Verification result must record:

- command
- exit code
- PASS/FAIL
- important failure summary
- whether failures are new or baseline/pre-existing

## §8 — Severity Scheme

| Severity | Meaning |
|---|---|
| CRITICAL | Security hole, data loss, destructive action, auth/payment/SSO breach, or break of a frozen invariant |
| HIGH | Functional bug, regression, data integrity issue, production incompatibility |
| MEDIUM | Correctness or robustness issue under edge conditions; important missing validation/test |
| LOW | Minor robustness issue, dead code, naming/doc mismatch that can mislead maintainers |

## §9 — Finding Types

| Type | Meaning | Destination |
|---|---|---|
| BUG | Reproducible defect with expected vs actual behavior | `docs/bugs/BUG-NNN-<slug>.md` |
| RISK | Plausible risk without full reproduction | `docs/review_findings.md` |
| QUESTION | Ambiguous behavior needing clarification | `docs/review_findings.md` |
| DESIGN-QUESTION | Potential issue involving frozen decision or architecture tradeoff | `docs/review_findings.md` |
| REVIEW-BLOCKER | Verification/review cannot establish baseline | banner in `docs/review_findings.md`, not a bug file |

## §10 — BUG File Template

One file per confirmed bug:

```text
docs/bugs/BUG-NNN-<kebab-slug>.md
```

Use this template:

```markdown
---
id: BUG-001
title: <one line>
severity: CRITICAL | HIGH | MEDIUM | LOW
status: OPEN
files:
  - path/to/file.ext
found: YYYY-MM-DD
---

## Summary
<what is wrong, 1-3 sentences>

## Invariant violated
<INV/Frozen/requirement reference and why it is violated>

## Location
- `file:line`

## Reproduction

### Input / setup
<exact input, state, request, command, or steps>

### Expected behavior
<what should happen>

### Actual behavior
<what happens instead>

## Evidence
<test output, code reference, diff reference, log excerpt, or concrete reasoning>

## Impact
<why it matters>

## Breakdown
- [ ] Add a regression test/manual verification that fails before the fix and passes after the fix
- [ ] Apply the minimal invariant-safe fix
- [ ] Run the verification commands listed in `CODE_REVIEW.md`
- [ ] Confirm no previously passing baseline test regressed

## Fix sketch
<minimal fix idea; reviewer does not apply it>

## Fix notes
<claude-fixer appends notes here>
```

Reviewer rules:

- `status: OPEN` is required.
- Leave every checklist item unchecked.
- Reviewer never writes `FIXED`.

Fixer rules:

- Flip `status: OPEN` → `status: FIXED` only when reproduced, fixed, regression-tested, and green relative to baseline.
- Add `resolved: YYYY-MM-DD` only after closure.

## §11 — Review Index Format

Write/refresh:

```text
docs/review_findings.md
```

Required sections:

```markdown
# Review Findings

> Optional REVIEW-BLOCKER banner if verification could not establish baseline.

## Review summary

- mode:
- scope:
- verification:
- reviewer:
- date:

## Summary counts

| Severity | Open | Fixed |
|---|---:|---:|
| CRITICAL | 0 | 0 |
| HIGH | 0 | 0 |
| MEDIUM | 0 | 0 |
| LOW | 0 | 0 |

## Bugs

| BUG | Severity | File | Gist | Status |
|---|---|---|---|---|

## Non-bug findings

### RISK

### QUESTION

### DESIGN-QUESTION

## Highest-priority remaining fix

- [BUG-NNN] <title or None>

## Verification commands

| Command | Exit code | Result | Notes |
|---|---:|---|---|
```

## §12 — Status Discipline

- Reviewer creates `OPEN` bugs only.
- Fixer closes bugs only after verification.
- Never delete bug files.
- Never reuse bug numbers.
- Never rename old bug files.
- Do not tick checklist items unless actually completed.
- Do not mark `FIXED` with partial verification.

## §13 — Re-review Policy

After `claude-fixer` fixes high-severity or low-confidence bugs, ask `codex-reviewer` to re-review the resulting diff.

The fixer must not call Codex itself.
