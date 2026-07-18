# Manifest

## Core

- `SKILL.md` — main Claude Code skill definition
- `README.md` — package overview and usage
- `INSTALL.md` — installation instructions
- `LICENSE-ATTRIBUTION.md` — upstream MIT attribution and notes

## Templates

- `templates/CLAUDE.template.md`
- `templates/README.template.md`
- `templates/CHANGELOG.template.md`
- `templates/env.example.template`
- `templates/.claude/settings.example.json`
- `templates/docs/PROJECT_OVERVIEW.template.md`
- `templates/docs/PROJECT_STATE.template.md`
- `templates/docs/REQUIREMENTS.template.md`
- `templates/docs/CONTEXT.template.md`
- `templates/docs/ARCHITECTURE.template.md`
- `templates/docs/DATA_MODEL.template.md`
- `templates/docs/API_SPEC.template.md`
- `templates/docs/DEVELOPMENT.template.md`
- `templates/docs/TESTING.template.md`
- `templates/docs/DEPLOYMENT.template.md`
- `templates/docs/SECURITY.template.md`
- `templates/docs/TROUBLESHOOTING.template.md`
- `templates/docs/PROCESS.template.md`
- `templates/docs/adr/ADR.template.md`

## Checklists

- `checklists/grilling-question-bank.md`
- `checklists/implementation-readiness.md`
- `checklists/docs-readiness.md`
- `checklists/security-readiness.md`
- `checklists/database-change-checklist.md`
- `checklists/api-contract-checklist.md`
- `checklists/deployment-readiness.md`
- `checklists/agent-handoff-checklist.md`

## Examples

- `examples/sample-output-tree.md`
- `examples/sample-first-run-prompt.md`

## Scripts

- `scripts/install-local.sh`


## Upstream Reference

- `upstream-reference/mattpocock-skills/grill-me-SKILL.md`
- `upstream-reference/mattpocock-skills/grill-with-docs-SKILL.md`
- `upstream-reference/mattpocock-skills/CONTEXT-FORMAT.md`
- `upstream-reference/mattpocock-skills/ADR-FORMAT.md`
- `upstream-reference/mattpocock-skills/LICENSE`


## v1.2 Additions

```txt
templates/.claude/agents/
├── codebase-cartographer.md
├── project-griller.md
├── docs-architect.md
├── api-contract-reviewer.md
├── data-model-reviewer.md
├── security-reviewer.md
├── deployment-reviewer.md
└── implementation-readiness-reviewer.md

checklists/subagent-delegation.md
```

These additions preserve the v1.1 grilling/docs behavior and add optional project-level subagent delegation.


## Added in v1.3

- `templates/.claude/agents/codex-review-coordinator.md`
- `templates/docs/PLAN.template.md`
- `templates/docs/PLAN-REVIEW-LOG.template.md`
- `templates/docs/CODEX_REVIEW.template.md`
- `templates/docs/IMPLEMENTATION_REVIEW_LOG.template.md`
- `checklists/codex-plan-review.md`
- `checklists/codex-code-review.md`
- `checklists/adversarial-review-rules.md`
- `checklists/claude-codex-mcp-diagnostics.md`
- `scripts/check-claude-codex-mcp.sh`
- MCP-first / Codex CLI / manual Codex review modes
