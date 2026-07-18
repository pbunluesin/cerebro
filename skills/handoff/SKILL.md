---
name: handoff
description: Create a concise, verified continuation checkpoint or cross-repository dispatch without duplicating Git history, requirements, plans, ADRs, or issue artifacts. Use only when the user explicitly asks to pause, clear context, continue in a new Codex or Claude session, hand work to another agent or repository, summarize the exact next action, or verify a dispatched API, data, event, queue, file, or sync contract. Update PROJECT_STATE.md for same-project continuation; use .cerebro/handoffs for source-owned cross-project deltas and an authorized target inbox pointer for delivery.
---

# Handoff

Preserve only context that the next agent cannot cheaply reconstruct from canonical files and Git. Invoke this skill explicitly; never create or mutate handoff state merely because a task appears nearly finished.

## Select mode

- `continuation` or no argument: update `PROJECT_STATE.md` for the next session.
- `dispatch <target> [--to <target-root>]`: write a source-owned cross-project delta and optionally deliver an inbox pointer to an explicitly authorized target root.
- `check [<dispatch-or-inbox-path>]`: summarize active dispatches addressed to this project or `all` without scanning unrelated directories.
- `done <dispatch>`: mark a dispatch done; never delete it automatically.
- `verify <dispatch>`: compare declared contracts with actual code.

Read [handoff-contract.md](references/handoff-contract.md) before writing or verifying.

## Collect evidence

1. Run `python3 scripts/collect_context.py --target <project-root>` from this skill directory before continuation, dispatch, or completion reporting.
2. If Python or the script is unavailable, inspect the branch, HEAD, status, staged and unstaged diffs, untracked files, and recent commits with read-only Git commands.
3. Treat the collected snapshot as evidence for this invocation only. Do not paste the full snapshot into `PROJECT_STATE.md` or a dispatch.
4. Inspect every file named as relevant before recording it. Never infer test results, runtime state, rejected approaches, or contract behavior from Git metadata alone.

## Continuation

1. Inspect Git branch, status, diff, recent commits, and relevant changed files.
2. Read the current `PROJECT_STATE.md` and canonical requirement/plan/finding artifacts.
3. Preserve the project's existing state layout and update `PROJECT_STATE.md` with only current information:
   - current objective and exact stopping point
   - verified in-progress state
   - current blockers and risks
   - decisions not yet captured elsewhere
   - inspected files and contracts that matter next
   - verified rejected attempts that would otherwise be repeated
   - transient runtime or environment state that cannot be reconstructed cheaply
   - exact run/verify commands
   - next explicit skill invocation and next safe action
4. Link to plans, ADRs, findings, commits, or docs rather than copying them.
5. Record environment variable names or service state only when required to continue; never record secret values.
6. Mark unknown or unverified facts explicitly.
7. Keep completed history out of state when Git or durable artifacts already preserve it.
8. Keep stable rejected decisions in the plan or ADR that owns them; use `Do not retry` only for a verified transient dead end, including evidence and the condition that would justify revisiting it.

Do not create a second same-project handoff file by default. `PROJECT_STATE.md` is the canonical continuation surface for Codex and Claude.

## Cross-project dispatch

1. Write the canonical dispatch under the source repository's `.cerebro/handoffs/` after the user requests the dispatch.
2. Name the file `<source>--<target>.md`.
3. Append a new dated `ACTIVE` entry when an active file already exists; do not overwrite unresolved work.
4. Include only the delta, required action, breaking changes, explicit contract changes, and evidence needed to locate the source of truth.
5. If `--to <target-root>` is requested, resolve the exact target and stop for explicit approval before writing outside the current project root. After approval, write only a pointer under `<target-root>/.cerebro/inbox/<source>--<target>.md`; keep the source dispatch canonical and do not duplicate its body.
6. Without an authorized target root, report the source dispatch path and verified Git ref for manual delivery. Never scan sibling repositories or the user's home directory to guess a destination.
7. Redact secrets and sensitive data.

## Check and completion

1. Check `.cerebro/inbox/` and `.cerebro/handoffs/` in the current project plus only paths the user supplied explicitly.
2. Resolve an inbox pointer to its canonical source dispatch before reporting action items. Report `NOT VERIFIED` if the source is inaccessible or ambiguous.
3. Mark `DONE (<date>)` only in the canonical source dispatch and add a verified commit or `No Git`.
4. Never delete or archive an entry automatically. Treat cleanup as a separate user-authorized action.

## Verify

1. Extract every declared HTTP, event, queue, file, database, or sync contract, including SQL Server stored procedure signatures and result sets when present.
2. Locate the actual authoritative definition in the available repository.
3. Report `MATCH`, `DRIFT`, `MISSING`, `UNDOCUMENTED`, or `NOT VERIFIED` with precise evidence.
4. Ask which side is authoritative when contract and code disagree. Never silently change either.

## Completion

Report the canonical file updated, any inbox pointer written, verified Git state, whether uncommitted changes remain, active blockers, and the recommended next invocation. Never claim a commit, test, runtime state, rejected approach, or decision that was not verified.
