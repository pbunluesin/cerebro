#!/usr/bin/env bash
#
# install-handoff-skill.sh (v2)
# Installs the user-scoped "handoff" skill for Claude Code.
# Scope: personal (~/.claude) -> available in EVERY project on this machine.
#
# v2 = original continuation handoff (fork context, git injection,
#      anti-hallucination rules) merged with:
#      - Matt Pocock's disciplines (no-duplication, redaction, suggested skills)
#      - kanly-style cross-repo dispatch + contract verify
#      - claude-mem de-duplication (no "Done" section, no git snapshots)
#      - status-based lifecycle (ACTIVE -> DONE, never delete; git optional)
#
# Invoke inside Claude Code (manual only):
#   /handoff [focus]          -> continuation handoff before /clear
#   /handoff write <target>   -> cross-repo dispatch
#   /handoff check            -> read pending dispatches
#   /handoff done <target>    -> mark dispatch DONE (+ git ref if available)
#   /handoff verify [file]    -> contract drift check (MATCH/DRIFT/MISSING/UNDOCUMENTED)
#
set -euo pipefail

# Respect a custom config dir if the user sets one; default to ~/.claude
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILL_DIR="$CLAUDE_DIR/skills/handoff"
SKILL_FILE="$SKILL_DIR/SKILL.md"

mkdir -p "$SKILL_DIR"

# Back up an existing skill before overwriting
if [[ -f "$SKILL_FILE" ]]; then
  backup="$SKILL_FILE.bak.$(date +%Y%m%d-%H%M%S)"
  cp "$SKILL_FILE" "$backup"
  echo "↳ Existing skill backed up to: $backup"
fi

# Quoted heredoc ('SKILL_MD') -> content is written literally.
# This is REQUIRED so $ARGUMENTS and the !\`git ...\` dynamic-injection
# markers are NOT expanded by this shell.
cat > "$SKILL_FILE" <<'SKILL_MD'
---
description: Session handoff, cross-repo dispatch, and contract verification. Invoke manually — /handoff (continuation before /clear), /handoff write <target>, /handoff check, /handoff done <target>, /handoff verify [file].
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(git branch:*), Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git config:*), Bash(ls:*), Bash(mkdir:*)
disable-model-invocation: true
argument-hint: [focus] | write <target> | check | done <target> | verify [file]
context: fork
---

## Current repository state
- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Recent commits: !`git log -5 --oneline`
- Diff stat: !`git diff --stat`
- Changed files: !`git diff --name-only`

If this project has no git repo yet, the lines above will be empty or errors.
Record `No git` where relevant. Never fabricate git state.

## Mode selection from $ARGUMENTS
- starts with `write <target>` -> DISPATCH
- equals `check`              -> CHECK
- starts with `done`          -> DONE
- starts with `verify`        -> VERIFY
- anything else (or empty)    -> CONTINUATION; treat the text as the focus area.

---

# Mode: CONTINUATION

Create or overwrite `.claude/handoff.md` so a fresh Claude Code session can
continue this work with minimal context loss.

Inspect touched files with Read/Grep/Glob only where needed to verify facts.

## Rules
- Write ONLY `.claude/handoff.md`. Do not modify source, config, tests, or docs.
- Use only facts from THIS session and the repo state injected above.
- Never invent decisions, completed work, commit hashes, test results, blockers, or file refs.
- If unknown/unverified, write `Unknown` or `Not verified` explicitly.
- Add `file:line` refs only for files you actually inspected.
- Do not duplicate content already captured in other artifacts (PRDs, plans,
  ADRs, CLAUDE.md, CODE_REVIEW.md, bug files, commits, diffs). Reference them
  by path instead.
- claude-mem runs on this machine. Do NOT include completed-work narration,
  test-run logs, commit lists, or session observations — claude-mem captures
  those automatically. There is intentionally NO "Done" section. Every line
  must be information the next session cannot get from the code, git,
  CLAUDE.md, or claude-mem.
- Do not snapshot git branch/status into the document — the next session runs
  git itself. Environment section covers services/config only.
- Redact secrets: API keys, passwords, connection strings, tokens, PII.
- Concise technical bullets, not narrative. Keep under ~120 lines.

## Output structure for .claude/handoff.md
# Handoff

## Goal
- Overall objective
- Task currently in progress
- Definition of done

## In Progress
- Exact current step, where work stopped
- Open files / uncommitted changes

## Key Decisions
- Decision: … | Why: … | Impact: …

## Rejected / Avoided
- Approach: … | Why rejected: … | Avoid repeating: …

## Relevant Files
- `path:line` — why it matters

## Environment
- Running services, required env vars/config, external deps
- Current assumptions

## Commands
### Run
```bash
# commands to continue development
```
### Verify
```bash
# commands to validate the work
```

## Gotchas
- Non-obvious constraints, edge cases, blockers, risky areas

## Suggested Skills
- Skills the next session should invoke, one-line reason each

## Next Actions
1. Next step  2. Next step  3. Validation

## After writing
Print: path written · branch (or `No git`) · uncommitted changes (yes/no) · recommended next command

---

# Mode: DISPATCH — `write <target>`

A delta note to a session working on ANOTHER repo. Not a session summary.

## Location
1. If `<repo-root>/.claude/handoffs/` exists -> repo mode: write there
   (committable, shareable with a team later).
2. Otherwise -> solo mode: write to `~/.claude/handoffs/` (works with or
   without git; create the directory if missing).

## Filename
`<source>--<target>.md`
- `<source>` = current repo directory name (repo mode with a team: use
  `git config user.name`, kebab-cased)
- `<target>` = repo/person/team from arguments, or `all`

If the file already contains an ACTIVE entry, APPEND under a `---` separator
with a new date header. Never overwrite an entry that is still ACTIVE.

## Format per entry
```markdown
# Dispatch: <target>
**From:** <source> · **Date:** <YYYY-MM-DD> · **Status:** ACTIVE

## <Short title of what changed>

### What changed
<1-3 bullets: the delta only>

### What the target must do
<Concrete action items>

### Breaking changes
<List, or "None">

### Contract
<Only if an interface changed. Declare it in table form using the contract
types defined in VERIFY, so `handoff verify` can check it later.>
```

## Rules
- Delta only, not full context. Actionable, not "FYI".
- Breaking changes flagged prominently.
- Redact secrets.
- In repo mode, suggest committing the file after writing.

---

# Mode: CHECK — `check`

1. List `.md` files in `<repo>/.claude/handoffs/` (if present) AND `~/.claude/handoffs/`.
2. Summarize entries with `Status: ACTIVE` addressed to this repo or `all`:
   from, date, action items, breaking changes.
3. State counts only for DONE entries and dispatches addressed to others —
   do not expand them.
4. If nothing is pending: "No pending dispatches for this repo."

---

# Mode: DONE — `done <target-or-file>`

Lifecycle is STATUS-BASED, never delete-based, because a project may not have
git initialized yet.

1. Locate the dispatch entry (most recent ACTIVE matching the argument; if
   ambiguous, list candidates and ask).
2. Edit `**Status:** ACTIVE` -> `**Status:** DONE (<YYYY-MM-DD>)`.
3. If the current repo has git, append below the status line:
   `**Ref:** <hash> <subject>` using the most recent commit related to the
   work (from `git log`). If no git, append `**Ref:** No git at completion`.
4. Never delete or compact an entry that is not marked DONE. Entries marked
   DONE may be compacted/removed later by the user — that cleanup is the
   user's call, not yours.
5. In repo mode, suggest committing the change.

---

# Mode: VERIFY — `verify [file]`

Check whether the actual code matches the contract declared in a dispatch.
Default target: the most recent ACTIVE dispatch addressed to this repo;
otherwise the file given in arguments.

## Contract types to extract and check
1. **HTTP/REST** — endpoint, method, request body shape, response shape, auth
   (Next.js route handlers, Nest.js controllers + DTOs, PHP handlers)
2. **SQL Server stored procedures** — procedure name, parameter names/types/
   direction, result-set columns (`CREATE OR ALTER PROCEDURE` in .sql files,
   migrations, sqlcmd scripts)
3. **BigQuery** — dataset.table, column names/types, SAFE_CAST expectations
   (SQL files, schema definitions, INFORMATION_SCHEMA references)
4. **Sync/event payloads** — field names, types, required/optional
   (TypeScript types/DTOs, Python dataclasses/pydantic models, JSON samples)

## Steps
1. Extract every declared contract from the dispatch.
2. Scan the codebase for the actual definition of each item (Grep/Glob/Read).
   If a contract lives in a sibling repo, ask for its path before reading
   outside the workspace.
3. Diff declared vs actual and report:

```
HANDOFF VERIFY: <dispatch title>

MATCH (N):
  ✓ <item> — declaration and code agree

DRIFT (N):
  ✗ <item> — declared: <X>, actual: <Y>
    Location: <file:line>

MISSING (N):
  ? <item> — declared in dispatch but not found in code

UNDOCUMENTED (N):
  + <item> — exists in code but no dispatch mentions it

VERDICT: N match, N drift, N missing, N undocumented
```

4. On drift/missing, ask which side is correct — fix the code to match the
   contract, or write a new dispatch updating the contract. Never silently
   change either. Base every finding on files actually read; if a contract
   type cannot be located, report `Not verified`, do not guess.
SKILL_MD

echo "✅ Installed: $SKILL_FILE"
echo "   Scope   : personal (all projects on this machine)"
echo "   Invoke  : /handoff [focus] | write <target> | check | done <target> | verify [file]"
echo "   Manual only; will not auto-trigger."
echo
echo "Next: restart Claude Code, then run  /skills  to confirm it loaded."
