# Project State

## Current status

- Phase: Audit remediation and release hardening
- Version: `0.1.0`
- Baseline: `1cecc13`; local `main` and `origin/main` were equal when verified
  on 2026-07-29
- Working tree: DBHS-02/DBEP-01 work and audit remediations are uncommitted
- Target agents: Claude Code for implementation/fixes; Codex for independent
  review

## Current objective

Resolve the verified findings in
`docs/quality/2026-07-28-cerebro-project-audit.md` without discarding the
existing SQL Server standards work, then provide evidence for review before any
commit or push.

## Confirmed decisions

- `.cerebro/project.json` is the canonical generated-project scaffold
  contract; `.cerebro/stack-profile.json` owns exact technology/rule
  provenance.
- Final validation derives its required-file plan from the project manifest.
  Caller flags are compatibility assertions only.
- Approved stack profiles require canonical installed inputs, exact
  catalog-shaped source refs, normalized project-relative paths, and
  `requirements-final:<YYYY-MM-DD>:<approver>`.
- Scaffold writes reject symlink targets/ancestors and validate the complete
  destination plan before the first write.
- Stack selection, status reporting, and final validation share fail-closed
  policy, light-review, full-review, and local-reference deadlines.
- Generated-project and audit scans share one ignored-directory policy.
- `DBHS-01` and `DBHS-02` are mandatory user-team SQL Server policy.
  `DBEP-01` is context-sensitive Microsoft-derived engineering guidance.
- `PROCESS.md` remains forbidden. `AGENTS.md` owns durable rules and this file
  owns current continuation state.

## Implemented in the working tree

- F-01: contained scaffold destinations with no-follow writes and negative
  symlink regression tests.
- F-02: hardened approval, source-ref, path, input-hash, and canonical-bundle
  provenance.
- F-03/F-04: added the canonical project manifest, reproducible stack-profile
  validation, caller-mismatch rejection, and normalized blocking-gap parsing.
- F-05: centralized freshness and made full semantic review expiry blocking.
- F-06/F-08: centralized scan pruning, detected ordinary `TBD`, exempted
  owned `TBD-NONBLOCKING`, and reconciled the Caveman migration note.
- F-07: added adversarial/positive readiness tests, scheduled freshness,
  non-masking shell validation, and pinned strict Claude plugin validation.
- Preserved and integrated DBHS-02, DBEP-01, four SQL object templates, and the
  expanded 326-rule catalogue from the pre-audit working tree.

## Latest verified evidence

Verified locally on 2026-07-29 after the remediation and documentation pass:

- `python3 -m unittest discover -s tests -p 'test_*.py' -v` — 47 tests passed.
- `python3 scripts/validate_all.py` — passed.
- `python3 scripts/validate_shell.py` — passed; no shell files.
- `python3 skills/create-project/scripts/check_stack_pack_status.py --as-of
  2026-07-29` — current; next light/policy review 2026-08-28 and full/local
  review 2026-10-28.
- `claude plugin validate . --strict` with Claude Code `2.1.210` — passed.
- `.github/workflows/validate.yml` parsed successfully with Ruby Psych and
  `git diff --check` passed.

## Current risks and blockers

- GitHub CLI credentials for the configured accounts were invalid when checked
  on 2026-07-29. This does not block local remediation; re-authentication is
  required before a future push.
- CI workflow behavior is locally reviewable but cannot be proven on GitHub
  until changes are committed/pushed and Actions runs.
- The independent audit report is retained as historical evidence; remediation
  status must be recorded as an addendum rather than rewriting its baseline.
- No commit or push is currently authorized.

## Backlog

1. Decide the public release/version/tag after forward testing.
2. Install or update this revision in user-scoped Claude Code/Codex locations
   only with separate explicit approval.
3. Decide whether to add or update optional RTK/Caveman integration for Codex;
   do not change the verified Claude setup as part of this work.
4. Add standards for uncovered SQL Server object naming only after the user
   provides the team convention.

## Next safe action

Present the verified uncommitted result to the user. Do not commit or push
without explicit approval.

## Handoff

- Exact stopping point: Audit fixes and preserved SQL Server additions are
  implemented and locally verified; GitHub CI/publication remain pending.
- Read first: this file, the audit report, `skills/create-project/SKILL.md`,
  and the changed scripts/tests.
- Do not touch: user-scoped Claude/Codex/RTK/Caveman configuration.
- Do not retry: GitHub authentication or publication without a user request.
- Runtime state: no service required; local Python and Claude validators are
  available.
- Next invocation: review the current diff, then commit/push only if explicitly
  authorized.
- Verify with: `python3 scripts/validate_all.py`,
  `python3 -m unittest discover -s tests -p 'test_*.py' -v`,
  `python3 scripts/validate_shell.py`,
  `python3 skills/create-project/scripts/check_stack_pack_status.py`, and
  `claude plugin validate . --strict`.
