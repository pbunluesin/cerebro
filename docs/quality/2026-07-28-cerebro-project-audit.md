# Cerebro project audit handoff — 2026-07-28

## Purpose

This is a review handoff for the primary Codex session. It records weaknesses
found during a read-only project audit. This session did not fix source code,
commit, or push anything.

## Audit scope and evidence boundary

- Verdict: **REVISE**
- Audited baseline: `1cecc13471807ca4f8032ef7e4abd2bf167e2a78`
  (`feat: add versioned stack packs and SQL Server house standard`)
- Branch at audit time: `main`, one commit ahead of `origin/main`
- Audit date: `2026-07-28`
- Evidence labels:
  - **VERIFIED** — reproduced or directly confirmed from code/test output.
  - **DOCUMENTED** — stated by project documentation but not independently
    exercised end to end.
  - **INFERRED** — architectural or product conclusion that needs an owner
    decision.

### Important current-state warning

After the audit was completed, the working tree acquired uncommitted changes in
several audited files, including the create-project scripts, references,
architecture documentation, README, and CHANGELOG. At the start of this handoff
session, the status snapshot also contained untracked SQL Server assets and
`temp/` content. The tree is being changed concurrently, so that snapshot may
already differ from the current status.

Therefore:

1. Treat every file/line reference below as a pointer into the audited baseline,
   not as proof of current behavior.
2. Re-run the reproduction on the current tree before changing anything; a
   finding may already be fixed, partially fixed, or moved to another line.
3. Inspect and preserve the existing uncommitted work. Do not overwrite it or
   use destructive Git cleanup.
4. This Markdown file is the only intended repository change from the audit
   handoff session.

## Remediation addendum — 2026-07-29

The original findings and baseline evidence below are preserved unchanged.
The primary session subsequently implemented the following uncommitted
remediations:

| Finding | Current remediation |
|---|---|
| F-01 | Resolved locally: every planned destination is contained and symlink-free before the first write; directory-relative no-follow writes and parent/destination escape tests were added. |
| F-02 | Resolved locally: approval records, exact catalog-shaped source refs, normalized project-relative globs, actual input hashes, and canonical approved bundles are enforced. |
| F-03 | Resolved locally: `.cerebro/project.json` is canonical; final validation recomputes the scaffold plan and stack selection from committed Cerebro inputs and rejects caller/tamper drift. |
| F-04 | Resolved locally: blocking-gap values are parsed and normalized after the colon; positive and negative final-readiness fixtures cover the behavior. |
| F-05 | Resolved locally: selector, extractor, status, and final validation enforce shared policy/light/full/local review deadlines; scheduled CI runs the real-date status gate. |
| F-06 | Resolved locally: validator and audit inventory use one directory-pruning policy and do not scan dependency/build trees. |
| F-07 | Implemented locally: 47 behavior tests include the negative paths above; CI adds scheduled freshness, non-masking shell checks, and pinned Claude `--strict` validation. A GitHub Actions run remains pending until publication. |
| F-08 | Resolved locally: ordinary `TBD` is audited while owned `TBD-NONBLOCKING` is allowed, Caveman identity is reconciled, and `PROJECT_STATE.md` now reflects the verified Git baseline and exact validator scope. |

Local evidence after remediation:

```text
python3 -m unittest discover -s tests -p 'test_*.py' -v
Ran 47 tests
OK

python3 scripts/validate_all.py
VALID: manifests=2 marketplaces=2 skills=9 python=ok assets=ok

python3 scripts/validate_shell.py
VALID: shell=none

python3 skills/create-project/scripts/check_stack_pack_status.py --as-of 2026-07-29
Stack Packs: current

claude plugin validate . --strict
Validation passed (Claude Code 2.1.210)
```

Manual adversarial replays also rejected the symlink escape without creating
an external file and rejected fabricated source refs and parent-traversal path
bindings without producing a profile. These claims remain local until the
working tree is reviewed, committed, and CI executes.

The owner also resolved the two product decisions: D-01 remains mandatory
user-team policy whenever SQL Server is selected, and D-02 is addressed by a
published supported-version matrix plus fail-closed rejection for unsupported
stack scopes.

## Executive summary

The project has solid nominal validation and a clear source-of-truth model, but
the current release gate is not yet fail-closed around filesystem containment,
stack-rule provenance, and generated-project readiness. The most important
issue is a reproducible scaffold escape through a symlink. Two additional high
severity findings allow fabricated rule provenance and caller-controlled
readiness validation to be reported as approved/valid.

The baseline should not be treated as release-ready until findings F-01 through
F-03 are resolved and covered by negative regression tests.

## Findings

### F-01 — CRITICAL — Project scaffolding can write outside the target through a symlink

Status: **VERIFIED**

Baseline pointers:

- `skills/create-project/scripts/bootstrap_project.py:130`
- `skills/create-project/scripts/bootstrap_project.py:229`

What was found:

- Target validation rejects `/` and the user's home directory, but it does not
  verify that destination ancestors are real directories contained within the
  selected target.
- The generation loop writes files without checking resolved destination paths
  or rejecting symlink ancestors.

Safe reproduction performed under `/private/tmp`:

1. Created a disposable target directory.
2. Made `target/docs` a symlink to a sibling `outside` directory.
3. Ran normal minimal scaffolding without force or merge behavior.
4. The command exited `0` and generated six documentation files in `outside`.

Impact:

- A crafted or pre-existing target tree can redirect scaffold output outside
  the authorized project root.
- This violates Cerebro's `WORKSPACE BOUNDARY` contract.
- Existing files outside the target could also be at risk depending on selected
  options and overwrite behavior.

Recommended fix:

- Resolve and validate every destination against the resolved target root before
  any write.
- Reject any existing symlink in the destination's ancestor chain.
- For stronger race resistance, use directory-relative opens and no-follow
  semantics where supported.
- Validate the complete write plan before creating the first file so failure is
  atomic from the user's perspective.

Required regression tests:

- Symlinked parent directory escaping to a sibling.
- Symlinked destination file.
- Nested symlink ancestor.
- A normal non-symlink target still scaffolds successfully.
- No external file is created or modified after rejection.

### F-02 — HIGH — Stack selector accepts fabricated provenance and unsafe path bindings as approved

Status: **VERIFIED**

Baseline pointers:

- `skills/create-project/scripts/select_stack_rules.py:106`
- `skills/create-project/scripts/select_stack_rules.py:119`
- `skills/create-project/scripts/select_stack_rules.py:189`

What was found:

- Source references are accepted when they contain a digit or hex-like value
  and avoid a small unstable-word list; they are not tied to a catalog entry,
  version, or authoritative source.
- Approval records are not validated against a structured approval contract.
- Stack path bindings can contain traversal such as `../../outside/**`.
- Custom catalog/policy inputs are accepted without proving that the recorded
  hashes describe the files actually used. In the reproduction, the resulting
  profile recorded the canonical catalog hash rather than the supplied custom
  catalog's hash.

Accepted reproduction inputs included:

```text
--stack nodejs@24.18.0
--path nodejs=../../outside/**
--source-ref nodejs=banana1
--approval-record x
--as-of 2026-07-28
```

Observed result:

```text
OK ... 41 rules (approved)
```

The generated profile contained:

```text
status: approved
approval_record: x
path: ../../outside/**
resolved source ref: banana1
```

Impact:

- Downstream consumers cannot rely on `approved` as evidence of provenance.
- Arbitrary path scopes can be attached to selected rules.
- Profiles can claim canonical catalog identity while being produced from
  different input content.

Recommended fix:

- Define and validate a structured source-reference schema tied to the selected
  technology/version and its catalog entry.
- Require a structured approval record with an auditable identity and expected
  fields.
- Normalize stack paths, require project-relative paths, and reject absolute
  paths and any `..` segment.
- Hash the actual catalog and policy files used and compare them to the profile.
- Recompute/verify bindings instead of trusting caller-provided resolved values.

Required regression tests:

- Reject fake refs such as `banana1`.
- Reject empty, malformed, or unverifiable approval records.
- Reject absolute and parent-traversal paths.
- Reject a custom catalog whose content/hash does not match recorded metadata.
- Preserve a valid approved selection as a positive control.

### F-03 — HIGH — Final readiness validation trusts caller flags and hand-edited profile content

Status: **VERIFIED**

Baseline pointers:

- `skills/create-project/scripts/validate_project.py:47`
- `skills/create-project/scripts/validate_project.py:210`

What was found:

- The validator receives `--profile`, `--agents`, `--features`, and `--stacks`
  from the caller instead of deriving them from a canonical generated-project
  manifest.
- It verifies that `selected_rule_ids` match IDs present in bindings, but does
  not establish that those IDs exist in the authoritative pack or are correct
  for the selected version/path.

Reproduction:

- A disposable generated-project fixture was edited to contain:
  - required documents replaced by `None`;
  - rule ID `FAKE-001`;
  - fabricated source and path bindings;
  - project state marked `critical`.
- Validation was invoked with caller-selected `--profile minimal --agents
  codex`.
- The validator printed `VALID`.

Impact:

- A hand-edited or incorrectly assembled project can pass the final
  implementation-readiness gate.
- The reported profile can differ from the project that was actually generated.
- Fabricated rule IDs and bindings can survive final validation.

Recommended fix:

- Generate a canonical machine-readable project manifest, for example
  `.cerebro/project-profile.json`, during scaffolding.
- Make final validation derive profile, agents, features, stacks, and expected
  artifacts from that manifest.
- Verify every rule ID and binding against the selected immutable pack/catalog,
  including version, source, and path scope.
- Validate actual requirement and acceptance evidence rather than only document
  presence or caller assertions.

Required regression tests:

- Tampered profile/manifest.
- Unknown rule ID.
- Valid ID attached to the wrong stack/version/path.
- Caller flags that conflict with the canonical manifest.
- A complete untouched generated project passes final validation.

### F-04 — MEDIUM — `Blocking gaps: None` is rejected due to regex backtracking

Status: **VERIFIED**

Baseline pointer:

- `skills/create-project/scripts/validate_project.py:147`

What was found:

The negative lookahead follows `\s*`. The regex engine can backtrack the
whitespace match to zero characters, evaluate the lookahead before the space,
and incorrectly treat the standard text below as a blocking gap:

```text
Blocking gaps: None
```

The malformed no-space form below passed:

```text
Blocking gaps:none
```

Recommended fix:

- Parse the value after the colon, trim it, then compare a normalized value to
  the allowed no-gap markers.
- Avoid a lookahead whose correctness depends on greedy whitespace.

Required regression tests:

- Standard `Blocking gaps: None` passes.
- Case/whitespace variants are handled intentionally.
- A real non-empty gap fails.
- Add at least one full positive final-readiness fixture.

### F-05 — MEDIUM — Quarterly full-review deadline is reported but not enforced

Status: **VERIFIED**

Baseline pointers:

- `skills/create-project/scripts/select_stack_rules.py:131`
- `skills/create-project/scripts/check_stack_pack_status.py:89`
- `skills/create-project/scripts/check_stack_pack_status.py:171`

What was found:

- Selection freshness checks cover policy and light catalog deadlines but ignore
  `next_full_review_at`.
- The status checker can print `full-review-due`, but returns non-zero only for
  `stale`.

Reproduction:

- Used a disposable catalog with future policy/light-review dates and a past
  full-review date.
- Status was `full-review-due` with exit code `0`.
- The selector still produced an `approved` profile.

Impact:

- Automation can continue approving selections after the project's documented
  full-review deadline.

Recommended fix:

- Define whether `full-review-due` is a blocking state. If the contract intends
  fail-closed behavior, reject selection and return non-zero.
- Centralize freshness calculation so the status checker and selector cannot
  diverge.
- Add a scheduled CI job that exercises the real current date and alerts before
  deadlines.

### F-06 — MEDIUM — Generated-project validation scans dependency and build trees

Status: **VERIFIED**

Baseline pointers:

- `skills/create-project/scripts/validate_project.py:95`
- `skills/create-project/scripts/validate_project.py:309`

What was found:

Markdown scans traverse almost every directory except `.git`. A disposable
`node_modules/dependency/README.md` containing template-like text produced eight
false validation errors.

Impact:

- Installed dependencies, vendored code, generated docs, or build output can
  make an otherwise valid project fail readiness checks.
- Results can change after dependency installation even when project-owned
  documentation is unchanged.

Recommended fix:

- Use one shared directory-pruning policy for every project scan.
- At minimum assess `.git`, `node_modules`, `.venv`, `venv`, `vendor`, `dist`,
  `build`, cache directories, coverage output, and generated artifacts.
- Prefer scanning the project-owned artifact list from the canonical manifest
  over an unrestricted recursive glob.

### F-07 — MEDIUM — CI covers nominal checks but misses the highest-risk failure paths

Status: **VERIFIED**

Baseline pointers:

- `.github/workflows/validate.yml:3`
- `AGENTS.md:62`

What was found:

- CI runs on push/pull request with Python 3.11 and 3.13 and executes
  `validate_all.py` plus unit tests.
- It does not exercise the strict Claude plugin validator, generated-project
  final-readiness paths, stack-selection tamper cases, scaffold containment, or
  scheduled freshness.
- The documented shell syntax command ends with `|| true`, which will mask a
  real syntax failure once shell scripts exist.

Recommended fix:

- Add negative tests for F-01 through F-06 to the standard test suite.
- Add a complete positive generated-project validation fixture.
- Add strict plugin validation where the required CLI can be installed
  deterministically.
- Add scheduled freshness validation.
- Enumerate shell files safely, but do not suppress genuine `bash -n` failures.

### F-08 — MEDIUM/LOW — Canonical status, migration notes, and token audit have drift

Status: **VERIFIED**

Baseline pointers:

- `PROJECT_STATE.md:51`
- `PROJECT_STATE.md:107`
- `docs/MIGRATION.md:54`
- `skills/create-project/scripts/audit_project.py:32`

What was found:

- `PROJECT_STATE.md` says all Codex plugin/skill validators passed, while its
  later validation notes say the external skill-creator validator was not run
  because PyYAML was unavailable. The scope of "all" is ambiguous.
- `docs/MIGRATION.md` says the exact identity of "Caseman" is unresolved, while
  `PROJECT_STATE.md` records it as confirmed Caveman.
- The unresolved-token regex detects `{{TOKEN}}` and `[TODO]`, but not ordinary
  `TBD`. A fresh draft containing multiple `TBD` markers reported
  `unresolved_tokens: 0`.
- Untracked `temp/db_standard/` material was present during the audit, creating
  an accidental `git add .` risk. It was not modified or deleted.

Recommended fix:

- Reconcile the current-state and migration statements or link both to one
  canonical decision record.
- Name validators precisely and distinguish project checks from unavailable
  external checks.
- Expand unresolved-marker detection using the project's documented marker
  vocabulary and add positive/negative tests.
- Decide whether `temp/` is intentional source, disposable local material, or
  ignored content; do not delete it without owner confirmation.

## Product and architecture decisions

These are not confirmed defects, but they should be resolved explicitly.

### D-01 — SQL Server house standard may be organization-specific

Status: **INFERRED — DECISION REQUIRED**

`DBHS-01` is automatically attached to every SQL Server selection, although the
content is presented as a team house standard. If Cerebro is intended as a
public/general plugin, organization-specific standards should likely be opt-in,
configurable, or clearly labeled rather than silently universal.

Baseline pointer:

- `skills/create-project/references/official-sources.json:265`

### D-02 — Product promise is broader than the explicit support matrix

Status: **INFERRED — DECISION REQUIRED**

The product describes grilling a "software idea", while explicit packs currently
cover a narrower web/backend stack set. Choose one:

- publish the supported stack matrix and reject unsupported stacks clearly;
- provide a deliberate `reference-only`/custom-stack path with lower assurance;
  or
- expand packs based on actual target users.

Avoid allowing unsupported technologies to look equally approved.

## Baseline validation evidence

The following passed on the audited baseline before the newer uncommitted
changes appeared:

```text
python3 scripts/validate_all.py
VALID: manifests=2 marketplaces=2 skills=9 python=ok assets=ok

python3 -m unittest discover -s tests -p 'test_*.py' -v
Ran 32 tests
OK

claude plugin validate . --strict
passed

python3 skills/create-project/scripts/check_stack_pack_status.py --as-of 2026-07-28
current
```

Recorded stack-pack versions and deadlines:

```text
best-practices: 2.1.0
anti-patterns: 2.1.0
policy: 1.0.0
catalog: 1.1.0
next light review: 2026-08-28
next full review: 2026-10-28
```

Tooling check at audit time:

```text
Codex 0.144.6
Claude 2.1.210
RTK 0.42.3
Caveman revision 655b7d9c5431
```

These baseline results must not be represented as validation of the current
uncommitted working tree. Re-run the full project validation after preserving
and understanding the current changes.

## Recommended remediation order

1. Re-verify F-01 on the current tree and close the filesystem boundary escape.
2. Make the selector/profile provenance chain fail-closed (F-02).
3. Add a canonical generated-project manifest and strengthen final readiness
   validation (F-03).
4. Land negative regression tests for F-01 through F-03 before broad refactoring.
5. Fix the deterministic validator/status defects in F-04 through F-06.
6. Expand CI coverage and remove masked failures (F-07).
7. Reconcile documentation/audit drift (F-08).
8. Record owner decisions for D-01 and D-02.
9. Run the required validation suite, inspect `git diff` and `git status -sb`,
   then request an independent Codex review according to `AGENTS.md`.

## Suggested verification suite after fixes

```bash
python3 scripts/validate_all.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/create-project/scripts/check_tooling.py --target .
```

Also:

- run `claude plugin validate . --strict` when that CLI is available;
- run the new containment, tamper, freshness, ignored-directory, and complete
  final-readiness regression cases;
- enumerate existing `*.sh` files before running `bash -n`, and fail on actual
  syntax errors;
- inspect `git diff --check`, `git diff`, and `git status -sb`.

## Audit limitations

- The audit did not semantically review every individual stack-pack rule.
- Remote initializers or third-party installation flows were not executed.
- No production data, credentials, external systems, or destructive operations
  were used.
- No source fix, commit, push, release, or PR was performed.
