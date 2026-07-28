# Reference Selection Gate

## Contents

1. Gate position
2. Evidence to resolve
3. Source selection
4. Fit review
5. Approval record
6. Freshness and update behavior

## Gate position

Run this gate after Final Requirements and before architecture or source-tree
materialization:

```text
REQUIREMENTS_READY
  -> STACK_CONFIRMED
  -> OFFICIAL_REFERENCES_RESOLVED
  -> REFERENCE_APPROVED
  -> ARCHITECTURE_READY
```

Do not select a scaffold from technology popularity alone. Resolve product
behavior, deployable units, runtime/deployment constraints, data ownership,
browser/support baselines, team constraints, and exact stack versions first.

## Evidence to resolve

Record:

- stack package/runtime and exact approved version or bounded range
- path and deployable-unit ownership
- target platform, database edition/compatibility level, and hosting constraints
- package manager and lockfile strategy
- required framework features and explicitly rejected optional features
- legacy compatibility constraints
- network/download writes required by an initializer

If any of these materially changes the scaffold or architecture and remains
unknown, the gate is `BLOCKED`.

## Source selection

Read [official-sources.json](official-sources.json) and select two to four
sources, each with one declared purpose:

1. official scaffold or official database-project initializer
2. official feature-specific example
3. official documentation or migration/support policy
4. approved house standard
5. mature open-source repository only when official sources do not answer an
   architecture question

Never use an arbitrary starter repository as the project source of truth.
Never treat an upstream default, canary, beta, RC, nightly, or preview branch as
the production baseline. Resolve and record the exact stable package/tag/ref at
use time.

The source catalogue is a routing index, not timeless evidence. Browse or
inspect the current authoritative source during every new-project gate because
versions, runtime minimums, examples, and initializer behavior can change.

## Fit review

For each candidate, record:

| Field | Required evidence |
|---|---|
| Purpose | Scaffold, feature example, normative behavior, migration, or house policy |
| Authority | Owner/maintainer and why it is authoritative |
| Resolved ref | Exact package version, tag, commit, or dated official docs |
| Compatibility | Runtime, framework, database, OS/tooling, and deployment fit |
| Writes | Files, dependency downloads, Git initialization, telemetry, and config changes |
| Imported decisions | Features or architecture the source would add |
| Rejected content | Demo code, services, dependencies, telemetry, or assumptions to remove |
| License | License and reuse constraints when code/assets are copied |
| Verification | Dry-run/help, install, build, type/lint, test, and diff checks |

Reject a candidate when its hidden decisions exceed the confirmed requirements,
its version is unresolved, its write behavior is unsafe, or its source is stale
and cannot be refreshed.

## Approval record

Store the compact human record in `docs/ARCHITECTURE.md`:

```markdown
## Approved references

| Purpose | Source | Resolved ref | Adopt | Reject/remove | Verified |
|---|---|---|---|---|---|
| Scaffold | <official URL> | <exact version/tag> | <specific files/conventions> | <demo/assumptions> | <date + evidence> |
```

Store the machine-readable resolved stack, path scopes, selected rule IDs, pack
version, approved source refs, exceptions, and freshness date in
`.cerebro/stack-profile.json`. Do not copy the full stack packs into generated
projects or duplicate their rules in `AGENTS.md`.

The approval record is not free text. Use:

```text
requirements-final:<YYYY-MM-DD>:<approver>
```

The date must not be later than profile resolution and the approver must be an
auditable person/team identity. Approved output may use only Cerebro's installed
canonical rule/policy/catalog bundle. Custom inputs are candidate-only until
reviewed into that bundle.

When SQL Server is selected, include every applicable approved local reference:
`DBHS-01` for stored procedures, `DBHS-02` for functions/triggers/types, and
`DBEP-01` for database design, normalization, indexes, and optimization. Store
each exact version, content hash, scope, and review deadline in the SQL Server
reference record. Do not label team policy as universal external best practice,
and do not turn context-sensitive engineering guidance into a blanket rule.

Run an official initializer only after showing its exact command, expected
writes, network/dependency impact, conflict behavior, and rollback path.

## Freshness and update behavior

Use [stack-version-policy.json](stack-version-policy.json) and the scripts under
`skills/create-project/scripts/` to resolve only rules matching the exact stack
version and path.

Run the offline status helper before browsing:

```bash
python3 skills/create-project/scripts/check_stack_pack_status.py
```

After verifying current upstream evidence, pass one exact `--source-ref` for
each selected catalog stack to `select_stack_rules.py`. Shared scopes such as
TypeScript and accessibility inherit their authoritative source IDs from the
version policy and do not need a catalog source ref.

- `observed_ref` records what a refresh discovered.
- `approved_ref` records what reviewed rules currently trust.
- A refresh may move `observed_ref`; it must not move `approved_ref`.
- Patch-only source metadata may use a fast review.
- New rules require a minor pack version and independent review.
- Level, scope, applicability, precedence, removal, or breaking generator
  changes require a major pack version and migration note.
- Run a light source review monthly, a semantic review quarterly, and an
  immediate review for a major release, support-policy change, critical
  advisory, initializer change, or normative accessibility update.
- Fail closed when a source deadline passes or a version-bound rule cannot be
  mapped. Report the exact refresh required; never silently fall back to a rule
  written for another version.
- Treat both light and full semantic review deadlines as blocking. The selector,
  status helper, and final validator share one freshness evaluator so their
  results cannot intentionally diverge.
