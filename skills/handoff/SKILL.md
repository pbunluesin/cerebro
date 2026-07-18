---
name: handoff
description: Create a concise, verified continuation checkpoint or cross-repository dispatch without duplicating Git history, requirements, plans, ADRs, or issue artifacts. Use when a user wants to pause, clear context, continue in a new Codex or Claude session, hand work to another agent/repository, summarize the exact next action, or verify that a dispatched API/data/event contract matches code. Update PROJECT_STATE.md for same-project continuation; use .cerebro/handoffs only for cross-project deltas.
---

# Handoff

Preserve only context that the next agent cannot cheaply reconstruct from canonical files and Git.

## Select mode

- `continuation` or no argument: update `PROJECT_STATE.md` for the next session.
- `dispatch <target>`: write a cross-project delta under `.cerebro/handoffs/`.
- `check`: summarize active dispatches addressed to this project or `all`.
- `done <dispatch>`: mark a dispatch done; never delete it automatically.
- `verify <dispatch>`: compare declared contracts with actual code.

Read [handoff-contract.md](references/handoff-contract.md) before writing or verifying.

## Continuation

1. Inspect Git branch, status, diff, recent commits, and relevant changed files.
2. Read the current `PROJECT_STATE.md` and canonical requirement/plan/finding artifacts.
3. Update `PROJECT_STATE.md` with only:
   - current objective and exact stopping point
   - verified in-progress state
   - current blockers and risks
   - decisions not yet captured elsewhere
   - exact run/verify commands
   - next safe actions
4. Link to plans, ADRs, findings, commits, or docs rather than copying them.
5. Mark unknown or unverified facts explicitly.
6. Keep completed history out of state when Git or durable artifacts already preserve it.

Do not create a second same-project handoff file by default. `PROJECT_STATE.md` is the canonical continuation surface for Codex and Claude.

## Cross-project dispatch

1. Create `.cerebro/handoffs/` if the user authorized the dispatch.
2. Name the file `<source>--<target>.md`.
3. Append a new dated `ACTIVE` entry when an active file already exists; do not overwrite unresolved work.
4. Include only the delta, required action, breaking changes, and explicit contract changes.
5. Redact secrets and sensitive data.

## Verify

1. Extract every declared HTTP, event, queue, file, database, or sync contract.
2. Locate the actual authoritative definition in the available repository.
3. Report `MATCH`, `DRIFT`, `MISSING`, `UNDOCUMENTED`, or `NOT VERIFIED` with precise evidence.
4. Ask which side is authoritative when contract and code disagree. Never silently change either.

## Completion

Report the file updated, verified Git state, whether uncommitted changes remain, active blockers, and the recommended next invocation. Never claim a commit, test, or decision that was not verified.
