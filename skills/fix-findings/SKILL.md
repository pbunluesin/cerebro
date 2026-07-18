---
name: fix-findings
description: Reproduce and fix confirmed code-review findings with minimal scoped changes, regression evidence, project verification, and explicit finding-state updates. Use when a user asks to fix review comments, bug finding files, CODE_REVIEW findings, reviewer output, or the highest-priority confirmed defect after review. Fix one finding at a time by default; do not use for speculative findings or broad refactoring.
---

# Fix Findings

Correct confirmed failures without turning a fix pass into redesign or cleanup.

## Select scope

1. Read the project guidance, requirements, relevant contracts, review contract, and finding.
2. Select one `OPEN` finding, highest severity first unless the user names another.
3. If multiple findings share one root cause and cannot be safely separated, explain the batch and obtain approval.
4. Stop if the finding lacks a concrete failure path, is stale, duplicates another finding, or conflicts with confirmed requirements.

## Reproduce and baseline

Read [fix-standard.md](references/fix-standard.md) in full.

1. Resolve the baseline commit and working-tree state.
2. Run the narrow reproduction or establish equivalent code/contract evidence.
3. Run relevant baseline checks before editing when feasible.
4. Record pre-existing failures separately.

Do not mark a finding fixed merely because the cited line changed.

## Implement

1. Identify the smallest correction that restores the violated requirement or invariant.
2. Preserve unrelated behavior, public contracts, data semantics, and accepted decisions.
3. Avoid dependency replacement, broad refactor, formatting sweep, or opportunistic cleanup.
4. Add or strengthen a regression test or explicit manual/contract verification that fails before and passes after the fix.
5. Update durable docs only if canonical behavior or operational procedure changed.

## Verify

Run in order:

1. reproduction/regression check
2. focused affected-module checks
3. project-required full verification
4. static, security, data, API, or migration checks required by the finding

Compare with baseline. A pre-existing failure does not excuse a new failure and should not be claimed as fixed.

## Update finding state

When a durable finding artifact exists:

- set `FIXED` only after the required evidence passes
- use `WONT_FIX` only with an explicit decision and rationale
- use `DUPLICATE` only with a canonical finding reference
- leave `OPEN` if verification is blocked or incomplete

## Report

Include:

- selected finding and reproduction
- root cause
- files changed and why
- tests/checks with exact results
- finding status
- pre-existing failures and skipped checks
- residual risk and re-review recommendation

In the default Cerebro delivery loop, Claude Code performs this fix workflow. Request a fresh Codex review after every R0/R1 fix and any security, auth, money, data, migration, concurrency, or external-contract change. Do not let the fixing context self-approve the correction.
