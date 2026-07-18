# Prompt: Run Codex Review

Use the `codex-reviewer` agent to review the selected diff/range.

Instructions:

- Read `CODE_REVIEW.md` first.
- Use DIFF mode unless I explicitly ask for AUDIT mode.
- Run verification commands from `CODE_REVIEW.md`.
- Ask Codex for structured findings.
- Write only review artifacts:
  - `docs/bugs/*.md`
  - `docs/review_findings.md`
- Do not edit application code, tests, configs, migrations, lockfiles, generated files, or CI files.
- Do not mark any bug as `FIXED`.

Review scope:

```text
[Describe branch, git range, or current uncommitted diff]
```
