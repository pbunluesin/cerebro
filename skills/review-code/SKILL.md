---
name: review-code
description: Review an explicit Git diff, branch range, pull request, commit, or repository scope for evidence-backed correctness, security, data-integrity, contract, concurrency, recovery, and maintainability defects. Use when a user asks for code review, Codex review, Claude review, regression analysis, release review, or a formal finding pass. Remain review-only, run relevant safe checks, and avoid modifying application code; use fix-findings for approved fixes.
---

# Review Code

Find material defects without contaminating independent review by fixing them.

## Scope and baseline

1. Read the closest `AGENTS.md` and project-specific review contract.
2. Resolve the exact scope: uncommitted diff, staged diff, commit, branch range, PR, or named files.
3. Record the baseline commit and any pre-existing failing checks.
4. Inspect the diff before the final file state; then read surrounding code and relevant callers/contracts.
5. Preserve unrelated working-tree changes and remain read-only.

## Review workflow

1. Read [review-standard.md](references/review-standard.md) in full.
2. When Claude Code is coordinating the workflow, read [claude-codex-loop.md](references/claude-codex-loop.md) in full and use Codex—not Claude self-review—for the independent finding pass.
3. Extract requirements, invariants, frozen decisions, acceptance criteria, and verification commands relevant to the scope.
4. Map changed inputs, outputs, side effects, persistence, privileges, and failure boundaries.
5. Run the smallest safe relevant checks first; run required full checks when feasible.
6. For each candidate, prove a concrete failure path from changed code or a directly affected contract.
7. Check whether the issue is new, pre-existing, duplicate, intentionally accepted, or outside scope.
8. Report only confirmed material findings. Keep test gaps or design suggestions separate when they are not defects.

## Finding contract

Include:

- severity
- concise title
- file and precise line/range
- triggering input/state/sequence
- observed or logically demonstrated failure
- impact and violated requirement/invariant
- minimal correction direction
- regression verification

Use `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` from the project review contract. If no contract exists, use the standard in the reference and disclose the fallback.

## Review artifacts

Write findings only when the user or project workflow requests durable artifacts. Use `docs/quality/findings/FINDING-NNN-<slug>.md` and keep one confirmed finding per file. Never change source, tests, migrations, dependencies, configuration, or generated output during review.

## Completion

Report:

- scope and baseline
- checks run and exact outcomes
- findings ordered by severity
- pre-existing or out-of-scope observations separately
- skipped checks and review limits
- reviewer provider, exact model ID, resolution evidence date, CLI version, and scope
- verdict: `APPROVED`, `REVISE`, or `BLOCKED`

No findings means no material defect was established in the reviewed scope; it does not prove the code is defect-free.
