# Prompt: Run Claude Fixer

Use the `claude-fixer` agent to fix one OPEN bug.

Instructions:

- Read `CODE_REVIEW.md` first.
- Fix one bug only unless I explicitly request a batch run.
- Default to the highest-priority OPEN bug in `docs/review_findings.md`.
- Reproduce before fixing.
- Add or finalize a regression test/manual verification.
- Run verification commands from `CODE_REVIEW.md`.
- Mark `FIXED` only when green relative to baseline.
- Never call Codex.

Target bug:

```text
[Highest-priority OPEN bug OR specific BUG-NNN]
```
