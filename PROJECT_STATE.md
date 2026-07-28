# Project State

## Current status

- Phase: Unified plugin implementation
- Version: `0.1.0`
- Readiness: Reference Selection Gate, versioned Stack Packs, and SQL Server stored procedure team standard implemented, validated, and committed locally
- Canonical plugin root: repository root
- Target agents: Codex and Claude Code

## Current goal

Consolidate the existing context pack, grilling skill, review/fix agents, handoff workflow, templates, and guardrails into one installable Cerebro plugin with shared skills and right-sized generated project profiles.

## Decisions

- Use one shared `skills/` tree for Codex and Claude.
- Keep separate `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` manifests.
- Make `create-project` the end-to-end entry point.
- Replace `PROCESS.md` with durable `AGENTS.md` guidance plus skill workflows.
- Keep `PROJECT_STATE.md` as a short, dynamic continuation point.
- Generate `minimal`, `standard`, or `critical` documentation profiles based on risk and complexity.
- Detect optional tools before offering installation; never install or mutate user-global configuration without explicit approval.
- Treat the project root as the deletion boundary; exact approval is required every time an action would delete/move/overwrite outside it.
- Use Claude Code for planning, implementation, and fixes; use the latest currently verified approved Codex model for independent review and high-risk re-review.
- Keep domain modeling, module/interface design, and architecture improvement as composable skills; `create-project` invokes them proportionally instead of duplicating their full guidance.
- Preserve Cerebro's canonical `docs/CONTEXT.md`, optional `docs/CONTEXT_MAP.md`, and `docs/decisions/` paths rather than adopting a second upstream layout.
- Keep same-project continuation in `PROJECT_STATE.md`; keep source-owned cross-project deltas under `.cerebro/handoffs/` and write only an approved pointer into a target inbox.
- Require explicit handoff invocation and collect Git state deterministically without copying reconstructable history into continuation context.
- Require `REFERENCE_APPROVED` after Final Requirements and before
  architecture/materialization.
- Keep Stack Pack source knowledge canonical under
  `skills/create-project/references/stack-packs/`; generated projects store only
  exact stack/path/source refs, selected rule IDs, and pack hashes in
  `.cerebro/stack-profile.json`.
- Separate upstream `observed_ref` from reviewed `approved_ref`; fail closed on
  stale catalogs, unsupported/excluded versions, ambiguous paths, or unmapped
  version-bound rules.
- Apply the supplied SQL Server stored procedure convention as versioned
  mandatory user-team policy (`DBHS-01`), not as a universal Microsoft best
  practice.
- Keep function, trigger, type, view, table, index, and other SQL Server object
  naming unresolved until the user provides those standards.

## Completed

- Implemented nine shared skills with progressive-disclosure references.
- Built project templates and deterministic bootstrap/validation scripts.
- Added Claude reviewer/fixer adapters and dual manifests.
- Added Codex and Claude marketplace manifests for GitHub installation.
- Passed internal validation, 32 behavior tests, all Codex plugin/skill validators, and strict Claude plugin/marketplace validation.
- Generated and draft-validated minimal, standard, and critical sample projects end to end.
- Verified all three generated profiles contain the safety contract and Claude-to-Codex review guidance.
- Structural audit reports one state file, no process file, no exact duplicates, and no unresolved template tokens.
- Compared current upstream Matt Pocock `grill-with-docs`, `grilling`, `domain-modeling`, `codebase-design`, and `improve-codebase-architecture` sources and adapted the evidence-backed gaps without vendoring them.
- Added inline domain-language capture, multi-context ownership mapping, compact ADR gates, deep-module/interface/seam evaluation, hotspot corroboration, candidate ranking, and selection-before-design controls.
- Refined handoff with explicit invocation, deterministic read-only Git context, compact operational continuation fields, authorized target inbox pointers, and detailed SQL Server stored procedure verification.
- Verified RTK `0.42.3` is installed and Claude-integrated without mutating its configuration.
- Confirmed “Caseman” means `JuliusBrussee/caveman` and added first-class detection/setup/isolation guidance.
- Verified Caveman is installed and enabled for Claude Code with active mode `full`.
- Verified neither RTK nor Caveman is currently configured for Codex on this machine.
- Moved the four temporary Stack Pack sources into canonical skill
  references/scripts and replaced the PyYAML generator boundary with
  dependency-free deterministic JSON.
- Added 289 version/path-aware Good/Bad rules across Node.js, TypeScript, PHP,
  Next.js, React, NestJS, Vue, Tailwind/accessibility, PostgreSQL, and SQL
  Server, including React/Nest/SQL Server gaps from the temporary pack.
- Added current official scaffold/docs/example routing, exact source-ref
  selection, monthly/quarterly/event-driven freshness policy, offline status
  reporting, and reviewed project-profile regeneration.
- Added `DBHS-01` standard version/hash/freshness enforcement, 16 exact
  SQL Server house-policy Good/Bad pairs, generated profile propagation,
  stack-conditional `docs/DATA.md` plus five SQL-only procedure templates, and
  SQL Server profile/scaffold consistency validation.
- Preserved the team-required GET `READ UNCOMMITTED`, non-GET transaction
  pattern, `IF NOT EXISTS`/existence checks, `RAISERROR` business validation,
  `THROW` propagation, naming, header, and formatting while documenting their
  known engine/concurrency trade-offs and required exception evidence.
- Verified the generated catalogue twice with zero warnings, validated all
  manifests/assets/skills, passed 32 unit tests, and passed strict Claude
  marketplace validation on 2026-07-28.

## In progress

- No implementation change remains. The Reference Gate, Stack Pack, and SQL
  Server house-standard work is validated and committed locally but not pushed.

## Open questions

- Whether to update the user-scoped Caveman installation from snapshot `655b7d9c5431`; upstream has moved since that snapshot, so the R1 user-global change requires separate explicit approval.
- Whether to add RTK and Caveman to user-scoped Codex configuration; neither is required for Codex review correctness.
- Decide whether the first public release should remain `0.1.0` or become `1.0.0` after forward testing.
- TypeScript 7.0 is current upstream but remains an observed candidate; the
  approved default is TypeScript 6.0.x until each selected framework, compiler
  API/plugin, lint, editor, and CI path is compatibility-reviewed.
- Node.js 26 is Current, not LTS; approved new production baselines remain exact
  Node.js 22 or 24 releases until the official LTS transition is reviewed.

## Backlog (deferred items 3–6)

3. Decide the public release/version/tag and publish migration notes after
   forward testing.
4. Install or update this Cerebro revision in the user-scoped Claude Code and
   Codex plugin locations only after separate explicit approval.
5. Decide whether to add or update optional RTK/Caveman integration for Codex;
   do not change the verified Claude setup as part of Stack Pack work.
6. Run the external skill-creator validator only after its missing PyYAML
   dependency installation is separately authorized; Cerebro's dependency-free
   pack generator and internal validators already cover this change.

## Next steps

1. Review the local Reference Gate/Stack Pack commit.
2. Provide function/trigger/type/other SQL Server object standards when ready;
   add each to the house source without inferring it from stored procedures.
3. Authorize push separately if the local commit is accepted.

## Handoff

- Exact stopping point: Reference Selection Gate, versioned Stack Packs,
  SQL Server procedure team standard, update lifecycle, selector, generated
  profile, conditional templates, validators, tests, and backlog are
  implemented, validated, and committed locally; changes are not pushed.
- Verified evidence: 289 generated rules with zero warnings;
  `scripts/validate_all.py` passed; all 32 unit tests passed; strict Claude
  marketplace validation passed; Stack Pack status is current through the
  2026-08-28 light-review deadline.
- Read first: `skills/create-project/SKILL.md`,
  `skills/create-project/references/reference-selection.md`,
  `skills/create-project/references/update-stack-packs.md`,
  `skills/create-project/references/official-sources.json`,
  `skills/create-project/references/stack-version-policy.json`,
  `skills/create-project/references/stack-packs/sqlserver-house-standard.md`
- Relevant contracts: `REFERENCE_APPROVED`, exact version/path/source
  selection, observed-versus-approved promotion, deterministic generation,
  stale-source failure, and `.cerebro/stack-profile.json`.
- Do not touch: User-scoped Codex or Claude plugin installation without explicit approval.
- Do not retry: The external `skill-creator` quick validator fails because PyYAML is absent; retry only after dependency installation is explicitly authorized. Cerebro's internal validator and dependency-free Stack Pack generator cover this change.
- Runtime/environment state: No service is required; Python 3, Git, Codex CLI, and Claude Code are present.
- Known gotchas: TypeScript 7 and Node.js 26 are observed but not blanket
  approved; DBHS-01 defines stored procedures only and other SQL Server object
  naming remains deliberately absent; a generated profile must be regenerated
  and reviewed when pack/standard hashes or versions change.
- Next invocation: Use `create-project` for a new project; it now grills through
  Final Requirements, official references, Stack Pack selection, architecture,
  structure materialization, and validation.
- Next command: No commit, push, plugin install/update, or user-global tooling
  change is authorized.
- Verify with: `python3 scripts/validate_all.py` and `python3 -m unittest discover -s tests -p 'test_*.py'`.
- Expected outcome: The same 289-rule deterministic catalogue, current source
  status, 32 passing tests, and no user-global or Git publication side effect.
