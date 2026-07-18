# PROCESS.md

This file is the workflow contract for the project.

## Purpose

`PROCESS.md` explains how work moves from planning to implementation, review, fixing, and approval.

It is not architecture documentation.
It is not business-rule documentation.
It is the operating process for human + AI collaboration.

## Default Workflow

```text
1. Human defines goal or issue
2. Claude reads PROJECT_STATE.md and relevant docs
3. Claude proposes implementation plan
4. Claude implements the change
5. Claude runs tests / lint / dry-run
6. Codex reviews the diff
7. Codex outputs findings and risk level
8. Claude applies valid fixes
9. Codex re-reviews if needed
10. Human approves final commit / PR
11. Claude updates PROJECT_STATE.md and docs
```

## Agent Responsibility Matrix

| Step | Owner | Notes |
|---|---|---|
| Requirement clarification | Human + Claude | Avoid over-building |
| Implementation | Claude | Main context owner |
| Code review | Codex | Independent second opinion |
| Fix review findings | Claude | Preserves implementation context |
| Final approval | Human | Required for important changes |
| Documentation update | Claude | Must update state/docs |

## Codex Review Policy

Codex should normally review only.

Codex may directly fix only low-risk mechanical issues:

- Formatting
- Typo
- Import cleanup
- Lint-only change
- Small test correction
- Documentation wording

Codex should not directly fix by default:

- Business logic
- API contract
- SQL/stored procedure
- Auth/security/payment logic
- Data migration
- Integration mapping
- Production deployment logic

## Completion Checklist

- [ ] Relevant tests/checks were run
- [ ] Codex review completed or intentionally skipped with reason
- [ ] Critical/high findings fixed
- [ ] Documentation updated if behavior changed
- [ ] `PROJECT_STATE.md` updated
- [ ] Human approval obtained for sensitive changes

## Review / Fix Workflow

For non-trivial changes, use this sequence:

```text
1. Claude implements
2. Claude runs local checks
3. codex-reviewer reviews the diff
4. codex-reviewer writes docs/bugs/ and docs/review_findings.md
5. claude-fixer fixes the highest-priority OPEN bug
6. Optional: codex-reviewer re-reviews the fix diff
7. Human approves R0/R1 or sensitive changes
```

Review/fix rules:

- `codex-reviewer` is review-only.
- `claude-fixer` is fix-only.
- `claude-fixer` fixes one bug per run by default.
- Batch fixing requires explicit request.
- High-severity fixes should be re-reviewed.

## Reversibility Policy

Before implementation, classify the change:

| Level | Meaning | Examples | Required Action |
|---|---|---|---|
| R0 | Irreversible or high-risk | production DB migration, payment/auth change, destructive data operation | Stop and ask for approval |
| R1 | Costly to reverse | API contract change, schema change, dependency replacement, vendor behavior change | Explain plan, risk, and rollback |
| R2 | Easy to reverse | typo, small UI text, local refactor, test-only change | Proceed and report |
