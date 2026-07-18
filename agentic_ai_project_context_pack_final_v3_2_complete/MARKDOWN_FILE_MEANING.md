# MARKDOWN_FILE_MEANING.md

## Purpose

This guide explains the meaning and responsibility of each Markdown file in Final v3.2.

## Core Principle

- `AGENTS.md` / `CLAUDE.md` = instruct AI agents
- `PROCESS.md` = define workflow
- `PROJECT_STATE.md` = track current state
- `docs/` = long-term project knowledge base
- `CODE_REVIEW.md` = code review contract
- `.claude/agents/` = project-scoped Claude subagents
- `.claude/rules/` = Claude-specific domain rules

## Root Files

| File | Meaning |
|---|---|
| `README.md` | Human onboarding and project overview |
| `AGENTS.md` | Shared AI agent instructions |
| `CLAUDE.md` | Claude Code project instructions |
| `PROCESS.md` | Workflow contract |
| `PROJECT_STATE.md` | Current project state and next actions |
| `CODE_REVIEW.md` | Review/fix contract for Codex reviewer and Claude fixer |
| `CODEX-REVIEWER.md` | Human-readable Codex reviewer role summary, if present |
| `CLAUDE-FIXER.md` | Human-readable Claude fixer role summary, if present |

## docs/

| File | Meaning |
|---|---|
| `docs/README.md` | Documentation index |
| `docs/architecture.md` | System architecture |
| `docs/data-flow.md` | Data movement and transformation |
| `docs/api-contract.md` | API endpoints and contracts |
| `docs/database-objects.md` | Database tables, views, stored procedures, indexes |
| `docs/integration-rules.md` | Vendor/system integration rules |
| `docs/security.md` | Auth, secrets, payment, PII, security behavior |
| `docs/guardrails.md` | AI operating guardrails |
| `docs/review-workflow.md` | Codex review / Claude fix process |
| `docs/testing-strategy.md` | Testing and verification strategy |
| `docs/observability.md` | Logs, metrics, dashboards, alerts |
| `docs/deployment-runbook.md` | Deployment and rollback |
| `docs/troubleshooting.md` | Debugging and known failures |
| `docs/review_findings.md` | Review findings index |
| `docs/bugs/BUG-NNN-*.md` | One bug report per finding |

## .claude/

| File | Meaning |
|---|---|
| `.claude/agents/codex-reviewer.md` | Project-scoped Codex review orchestrator |
| `.claude/agents/claude-fixer.md` | Project-scoped Claude fixer |
| `.claude/rules/*.md` | Claude-specific rules by domain |
| `.claude/MEMORY.local.template.md` | Local memory template; do not commit filled memory |

## Rule of Thumb

If the content is:
- Instruction for AI → `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`
- Current status → `PROJECT_STATE.md`
- Workflow → `PROCESS.md`
- Durable system knowledge → `docs/`
- Code review contract → `CODE_REVIEW.md`
- Review result → `docs/review_findings.md`, `docs/bugs/`
- Personal/local lesson → `.claude/MEMORY.local.md` and do not commit it
