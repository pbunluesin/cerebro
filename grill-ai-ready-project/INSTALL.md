# Install Instructions

## Personal install

Use this when you want the skill available across all projects.

```bash
mkdir -p ~/.claude/skills
cp -R grill-ai-ready-project ~/.claude/skills/grill-ai-ready-project
```

## Project install

Use this when you want the skill versioned inside a specific repo.

```bash
mkdir -p .claude/skills
cp -R grill-ai-ready-project .claude/skills/grill-ai-ready-project
```

## Verify

Open Claude Code in a project root and run:

```txt
/grill-ai-ready-project --audit-existing
```

## Recommended first run for a production project

```txt
/grill-ai-ready-project --production "<project summary, tech stack, business goal>"
```


## Optional: Install Subagent Templates Into a Project

After running the skill in a project, copy selected subagent templates into the project repo if you want project-level Claude Code subagents:

```bash
mkdir -p .claude/agents
cp ~/.claude/skills/grill-ai-ready-project/templates/.claude/agents/*.md .claude/agents/
```

For production projects, keep all included agents. For small projects, `project-griller`, `docs-architect`, and `implementation-readiness-reviewer` are usually enough.


## Optional: Check Claude / Codex / MCP Setup

Run from any terminal:

```bash
~/.claude/skills/grill-ai-ready-project/scripts/check-claude-codex-mcp.sh
```

Inside Claude Code, also run:

```txt
/mcp
```

If Codex appears as an MCP server/tool, use `--mcp-first`. If not, use `--codex-cli` or `--manual-codex`.
