---
name: review-plan
description: Adversarially review an implementation plan against confirmed requirements, architecture, contracts, data ownership, security, operations, rollback, and validation before code is written. Use when a user asks for a plan review, second opinion, pre-implementation gate, architecture challenge, Codex review of a Claude plan, or Claude review of a Codex plan, especially for auth, payments, migrations, integrations, concurrency, or production risk. Remain read-only unless the user separately asks the planner to revise.
---

# Review Plan

Challenge the plan independently. Do not reward length, confidence, or template completeness.

## Establish review independence

- Read the actual plan, requirements, relevant docs, contracts, and repository evidence.
- Do not rely only on the planner's summary.
- If possible, use a different agent/provider or a fresh context from the planner.
- If independence is not available, disclose that limitation; do not claim cross-model review.
- Do not modify the plan or implementation files during the review.
- In the default Cerebro loop, Claude Code creates/revises the plan and Codex performs this independent review. Resolve and record the latest approved Codex model from current authoritative evidence; do not silently substitute Claude self-review.

## Workflow

1. Identify the exact plan version and review scope.
2. Read `AGENTS.md`, `PROJECT_STATE.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, and only the relevant conditional documents.
3. Extract confirmed requirements, invariants, accepted assumptions, frozen decisions, and acceptance criteria.
4. Read [plan-review-standard.md](references/plan-review-standard.md) in full.
5. Trace each planned step to a requirement and observable validation.
6. Test the plan against happy, failure, partial-failure, retry/replay, concurrency, migration, rollback, and operational scenarios as applicable.
7. Prefer simpler, safer alternatives when they meet the same confirmed requirements.
8. Report only material issues. Separate blockers, non-blocking improvements, and questions caused by missing evidence.
9. Record reviewer provider, exact model ID, resolution evidence date, CLI version, and scope.

## Finding format

For every material finding include:

- severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- affected plan step and requirement/invariant
- concrete failure scenario
- impact
- evidence from project artifacts
- minimal plan correction
- validation that would prove the correction

Do not invent application code or implementation details absent from the repository.

## Verdict

End with exactly one:

- `VERDICT: APPROVED` — no material issue remains and validation/rollback coverage is sufficient.
- `VERDICT: REVISE` — one or more material issues have concrete corrections.
- `VERDICT: BLOCKED` — authoritative requirements, contracts, or evidence needed for review are missing.

Approval means the plan is safe enough to implement, not that production readiness is guaranteed.
