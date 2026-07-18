# Install Review Agents — Claude Code User Scope

Use this when you want `codex-reviewer` and `claude-fixer` available across all projects on the same machine.

## Prerequisites

- Claude Code is installed and working.
- Codex MCP is configured if you want `codex-reviewer` to call Codex.
- Your project contains a filled `CODE_REVIEW.md`.

## Install Steps

From the extracted pack root:

```bash
mkdir -p ~/.claude/agents
cp project-root/.claude/agents/codex-reviewer.md ~/.claude/agents/codex-reviewer.md
cp project-root/.claude/agents/claude-fixer.md ~/.claude/agents/claude-fixer.md
```

Restart Claude Code so the new subagents are loaded.

Verify in Claude Code:

```text
/agents
```

You should see:

- `codex-reviewer`
- `claude-fixer`

## Project Scope Alternative

For repo-specific behavior, keep them in:

```text
project-root/.claude/agents/
```

Project scope is recommended when the workflow is tightly coupled to the repo's `CODE_REVIEW.md` and docs.

## Recommended Invocation

Review current diff:

```text
Use the codex-reviewer agent to review the current uncommitted diff in DIFF mode. Follow CODE_REVIEW.md. Review only. Do not modify application code.
```

Fix highest-priority OPEN bug:

```text
Use the claude-fixer agent to fix the single highest-priority OPEN bug from docs/review_findings.md. Follow CODE_REVIEW.md. Fix one bug only.
```
