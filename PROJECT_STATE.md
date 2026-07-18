# Project State

## Current status

- Phase: Unified plugin implementation
- Version: `0.1.0`
- Readiness: Core plugin, safety contract, and domain/design/architecture workflows validated; optional machine-level updates pending approval
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
- Verified RTK `0.42.3` is installed and Claude-integrated without mutating its configuration.
- Confirmed “Caseman” means `JuliusBrussee/caveman` and added first-class detection/setup/isolation guidance.
- Verified Caveman is installed and enabled for Claude Code with active mode `full`.
- Verified neither RTK nor Caveman is currently configured for Codex on this machine.

## In progress

- Review the complete replacement diff and obtain explicit authorization before committing, pushing, or changing user-scoped tooling.

## Open questions

- Whether to update the user-scoped Caveman installation from snapshot `655b7d9c5431`; upstream has moved since that snapshot, so the R1 user-global change requires separate explicit approval.
- Whether to add RTK and Caveman to user-scoped Codex configuration; neither is required for Codex review correctness.
- Decide whether the first public release should remain `0.1.0` or become `1.0.0` after forward testing.

## Next steps

1. Run Dissent and full diff review before any commit.
2. Decide whether the optional user-scoped Caveman update and Codex integrations are wanted.
3. Push only after explicit authorization so GitHub marketplace install commands resolve this release.
