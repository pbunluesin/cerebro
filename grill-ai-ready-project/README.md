# grill-ai-ready-project

A Claude Code skill for turning vague project ideas into AI-ready engineering projects.

It combines requirement grilling, shared language, ADR capture, project state management, security/deployment/testing readiness, and project-standard Markdown generation.

## Install

Copy this folder to your personal Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R grill-ai-ready-project ~/.claude/skills/grill-ai-ready-project
```

Then restart Claude Code or reload skills if your agent supports it.

## Usage

```txt
/grill-ai-ready-project "Build a Next.js + Node.js + SQL Server payment platform on GCP"
```

Modes:

```txt
/grill-ai-ready-project --grill-only "New SSO integration"
/grill-ai-ready-project --docs-only "Use existing conversation context"
/grill-ai-ready-project --audit-existing
/grill-ai-ready-project --production "Vendor API sync project"
/grill-ai-ready-project --small "Internal Python utility"
```

## Recommended workflow

1. Run this skill before implementation.
2. Answer one grilling question at a time.
3. Let the agent create/update Markdown docs.
4. Review generated docs.
5. Ask the agent to create an implementation plan.
6. Implement one vertical slice at a time.
7. Update `docs/PROJECT_STATE.md` and `CHANGELOG.md` after each meaningful change.

## Included resources

- `templates/`: Markdown templates to materialize into project docs
- `checklists/`: readiness and review checklists
- `examples/`: sample output structure and first-run prompts
- `scripts/install-local.sh`: optional local install helper

## Attribution

See `LICENSE-ATTRIBUTION.md`.


## v1.3 Codex Review Layer

This version adds optional cross-model review before implementation. Use it when work is high-risk or when you want Codex to challenge Claude's plan independently.

Recommended MCP-first usage:

```txt
/grill-ai-ready-project --grill-only --production --codex-plan-review --mcp-first "Payment Platform using Next.js, Node.js, SQL Server, GCP. Grill requirements first, then produce PLAN.md and have Codex review it before code."
```

Fallback modes:

```txt
/grill-ai-ready-project --codex-review-only --mcp-first "Review existing PLAN.md before implementation."
/grill-ai-ready-project --codex-review-only --codex-cli "Review existing PLAN.md using local Codex CLI."
/grill-ai-ready-project --codex-review-only --manual-codex "Generate a manual Codex review prompt."
```

Diagnostics:

```bash
~/.claude/skills/grill-ai-ready-project/scripts/check-claude-codex-mcp.sh
```
