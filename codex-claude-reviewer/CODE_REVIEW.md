# CODE_REVIEW.md — Review brief

Drives every code-review pass (codex-reviewer). Grounded in `CLAUDE.md`, `AGENTS.md`, and
`.claude/rules/*`. Review against this brief; do not improvise a generic review.

## §0 — Scope


## §1 — Frozen / do-NOT-flag (deliberate decisions)



## §2 — Priority hunt list



## §3 — Verification commands

## §4 — Severity scheme

- **CRITICAL** — security hole, data loss, or breaks a frozen invariant (esp. F-002, no-raw-SQL, GUID-only URLs).
- **HIGH** — functional bug, regression, incompatibility that breaks production.
- **MEDIUM** — correctness/robustness issue under edge conditions; a11y/no-JS breakage.
- **LOW** — minor robustness, dead code, naming, or doc mismatch.

## §5 — Bug-file template

One file per finding: `docs/bugs/BUG-NNN-<slug>.md` (zero-padded NNN, increment from the highest existing).

```markdown
---
id: BUG-001
title: <one line>
severity: CRITICAL | HIGH | MEDIUM | LOW
status: OPEN
files: [public/action.php]
found: 2026-06-22
---

## Summary
<what's wrong, 1-3 sentences>

## Reproduction / evidence
<file:line refs; how it manifests>

## Impact
<why it matters; which invariant/checklist item>

## Suggested fix
<minimal change; do NOT apply it — reviewer never edits code>

## Fix checklist
- [ ] Fix applied
- [ ] Regression test / manual verification
- [ ] `php -l` clean
```

`status: OPEN` is required — the fixer flips it to `FIXED`.

## §6 — Report format

After writing the per-finding files, write/refresh `docs/review_findings.md`: a summary table
(`| BUG | Severity | File | Gist | Status |`) + the verification commands you ran and their result.
