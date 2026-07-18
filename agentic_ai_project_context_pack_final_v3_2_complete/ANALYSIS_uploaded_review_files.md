# Analysis: Uploaded Review/Fix Markdown Files

## Files analyzed

- `codex-reviewer.md`
- `claude-fixer.md`
- `CODE_REVIEW.md`

## Verdict

The design is strong and should be integrated.

Recommended integration:

- Put `codex-reviewer.md` under `.claude/agents/codex-reviewer.md`
- Put `claude-fixer.md` under `.claude/agents/claude-fixer.md`
- Put the review brief at repo root as `CODE_REVIEW.md`
- Add `docs/review-workflow.md`
- Add `docs/review_findings.md`
- Add `docs/bugs/`

## Key strengths

### `codex-reviewer.md`

- Strong separation between Claude orchestrator and Codex reviewer.
- Uses `CODE_REVIEW.md` as single source of truth.
- Review artifacts only; no application code edits.
- Supports DIFF and AUDIT modes.
- Requires verification output as review evidence.
- Requires reproduction gate for BUG findings.
- De-duplicates existing bugs.
- Self-checks working tree mutation before reporting completion.

### `claude-fixer.md`

- Strong fixer boundary: Claude is sole author of fixes.
- Never calls Codex.
- Fixes one bug per run by default.
- Requires reproduction before implementation.
- Adds regression test/manual verification.
- Uses baseline-relative verification.
- Prevents closing bugs when new regressions are introduced.
- Tracks overlap during multi-bug runs.

### `CODE_REVIEW.md`

- Good high-level idea but originally too sparse.
- Needed expansion to align with reviewer/fixer expectations.

## Main adjustment made in Final v3.2

The uploaded `CODE_REVIEW.md` template was expanded because `codex-reviewer` and `claude-fixer` expect richer fields than the original brief provided.

Final v3.2 `CODE_REVIEW.md` now includes:

- workflow
- read-first files
- scope
- frozen decisions
- domain invariants
- priority hunt list
- out-of-scope rules
- verification commands
- severity scheme
- finding types
- detailed bug-file template
- review index format
- status discipline
- re-review policy

## Risk notes

- `codex-reviewer` requires Codex MCP tools to be configured.
- Project teams must fill `CODE_REVIEW.md`; the template alone is not enough.
- User scope install is convenient but project scope is safer for repo-specific instructions.
- Do not use batch fixing unless explicitly requested.
