# Finding Fix Standard

## Contents

1. Valid finding gate
2. Minimal-fix rules
3. Regression evidence
4. High-risk corrections
5. Closure gate

## Valid finding gate

Before editing, confirm:

- the cited code and requirement/invariant still exist
- the triggering condition is reachable
- the failure is not baseline-only or already corrected
- the requested fix belongs to the user's authorized scope
- the proposed behavior does not contradict an accepted decision

If any item fails, do not force a code change to satisfy the wording of a stale finding. Update or reject the finding with evidence.

## Minimal-fix rules

- Change the narrowest ownership layer that can enforce the invariant consistently.
- Prefer existing patterns that are correct in the same repository.
- Avoid adding abstraction for a single use unless it closes a meaningful boundary.
- Do not weaken validation, authorization, constraints, or tests to make checks pass.
- Do not catch and suppress errors without preserving visibility and correct state.
- Do not change public contracts unless the finding and approved requirements require it.
- Preserve generated files; change their source generator instead.
- Keep formatting changes limited to touched code unless a required formatter acts more broadly.

## Regression evidence

Strong evidence demonstrates the failure before and correct behavior after.

Prefer:

1. focused automated regression test
2. contract/integration test at the ownership boundary
3. deterministic reproduction script or fixture
4. static proof plus targeted command when execution is unavailable
5. explicit manual steps with observable results as a last resort

A test that passes both before and after without exercising the failure is not regression evidence.

## High-risk corrections

### Authorization

Test allowed and denied actors, resource ownership, tenant boundary, privilege changes, and audit evidence. Do not rely only on UI hiding.

### Data and migration

Verify constraints, transaction boundaries, idempotency, representative data, dry run, reconciliation, and rollback/forward recovery. Require explicit approval for destructive execution.

### Payment or external effects

Verify duplicate/replay handling, authoritative state, partial failure, reconciliation, and operator visibility. Do not re-send real external effects during tests.

### Concurrency

Use a deterministic interleaving or invariant-focused test. A single sequential happy-path test is insufficient.

### Production configuration

Separate code correction from deployment. Verify configuration shape without applying to production unless explicitly authorized.

## Closure gate

Set `FIXED` only when:

- the original failure is no longer reproducible for the intended reason
- regression evidence fails on the baseline or otherwise proves the corrected invariant
- focused checks pass
- required full checks pass or documented baseline-equivalent exceptions are accepted
- no new contract, security, data, or operational regression is introduced
- documentation and state are consistent

Recommend independent re-review for critical/high findings, security boundaries, migrations, concurrency, and corrections with broad blast radius.
