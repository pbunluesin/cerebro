# Project State

## Current status

- Phase: Unified plugin implementation
- Version: `0.1.0`
- Readiness: `0.1.0` baseline published at `e1e9bc8`; handoff contract refinement implemented and validated
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

## Completed

- Implemented nine shared skills with progressive-disclosure references.
- Built project templates and deterministic bootstrap/validation scripts.
- Added Claude reviewer/fixer adapters and dual manifests.
- Added Codex and Claude marketplace manifests for GitHub installation.
- Passed internal validation, fifteen behavior tests, all Codex plugin/skill validators, and strict Claude plugin/marketplace validation.
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

## In progress

- No implementation change is currently in progress; reference-selection and stack-pack design remain consultation topics.

## Open questions

- Whether to update the user-scoped Caveman installation from snapshot `655b7d9c5431`; upstream has moved since that snapshot, so the R1 user-global change requires separate explicit approval.
- Whether to add RTK and Caveman to user-scoped Codex configuration; neither is required for Codex review correctness.
- Decide whether the first public release should remain `0.1.0` or become `1.0.0` after forward testing.

## Next steps

1. Decide whether to add a Reference Selection Gate between final requirements and architecture.
2. Define stack-pack scope and source-selection policy before adding stack-specific guidance.
3. Select the next release version before tagging or reinstalling the plugin so caches cannot hide the update.

## Handoff

- Exact stopping point: Handoff refinement is implemented and validated; no further Handoff change is currently planned.
- Verified evidence: `scripts/validate_all.py` passed; Claude strict plugin validation passed; all 19 unit tests passed; the Git collector separated staged, unstaged, and untracked state in repository and temporary-worktree tests.
- Read first: `skills/handoff/SKILL.md`, `skills/handoff/references/handoff-contract.md`, `skills/create-project/assets/project/PROJECT_STATE.md.tmpl`, `tests/test_handoff.py`
- Relevant contracts: Same-project continuation, cross-project dispatch delivery, SQL Server stored procedure verification, and explicit invocation policy.
- Do not touch: User-scoped Codex or Claude plugin installation without explicit approval.
- Do not retry: The external `skill-creator` quick validator fails because PyYAML is absent; retry only after dependency installation is explicitly authorized. Cerebro's internal validator covers the required frontmatter, metadata, links, scripts, and contract markers.
- Runtime/environment state: No service is required; Python 3, Git, Codex CLI, and Claude Code are present.
- Known gotchas: A draft `PROJECT_STATE.md` must not contain the literal implementation-ready state marker inside explanatory text because the readiness validator treats that marker as evidence.
- Next invocation: Use `create-project` only after the Reference Selection Gate scope is approved, or invoke `handoff` explicitly when a real continuation/dispatch is required.
- Next command: No implementation command is currently authorized.
- Verify with: `python3 scripts/validate_all.py` and `python3 -m unittest discover -s tests -p 'test_*.py'`.
- Expected outcome: A separately approved Reference Selection Gate or stack-pack design, without expanding the completed Handoff scope.
