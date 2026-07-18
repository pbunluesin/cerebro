# PUBLIC_REPO_USAGE.md

## Purpose

This guide explains how a general user should use Final v3.2 when it is hosted as a public GitHub repository.

Final v3.2 is not an application starter template. It is an AI-agent-ready documentation and workflow scaffold.

Use it to prepare a new or existing project for Claude Code, Codex review, and durable project context.

## Recommended Quick Start

```bash
git clone https://github.com/<owner>/agentic-ai-project-context-pack.git
cd agentic-ai-project-context-pack

mkdir ../my-new-project
cd ../my-new-project
git init

cp -R ../agentic-ai-project-context-pack/project-root/. .
```

## First Claude Code Prompt

```text
Read AGENTS.md, CLAUDE.md, PROCESS.md, PROJECT_STATE.md, CODE_REVIEW.md, and docs/README.md.

Then inspect the repository structure and summarize:
1. What this project is
2. What context is still missing
3. Which docs need to be filled first
4. Any risk before implementation

Do not modify code yet.
Only propose an initialization plan.
```

## Initialize Docs Prompt

```text
Initialize the project documentation using the Final v3.2 structure.

Fill in the docs based on the current repository:
- PROJECT_STATE.md
- docs/architecture.md
- docs/data-flow.md
- docs/api-contract.md
- docs/database-objects.md
- docs/integration-rules.md
- docs/security.md
- docs/testing-strategy.md
- docs/observability.md
- docs/deployment-runbook.md
- docs/troubleshooting.md
- CODE_REVIEW.md

Rules:
- Do not invent missing facts.
- Mark unknown items as TODO.
- Do not modify application code.
- Keep AGENTS.md and CLAUDE.md concise.
- Put deep project knowledge in docs/.
```

## Normal Workflow

1. Human defines task.
2. Claude reads state/docs.
3. Claude implements.
4. Claude runs verification.
5. Codex reviewer reviews diff.
6. Claude fixer fixes one OPEN bug.
7. Codex re-review if needed.
8. Human approves commit.
9. Claude updates PROJECT_STATE.md and docs/.

## Code Review Prompt

```text
Use the codex-reviewer agent to review the current uncommitted diff in DIFF mode.
Follow CODE_REVIEW.md.
Review only.
Do not modify application code.
```

## Fix Prompt

```text
Use the claude-fixer agent to fix the single highest-priority OPEN bug from docs/review_findings.md.
Follow CODE_REVIEW.md.
Fix one bug only.
```

## Anti-patterns

- Do not let AI invent missing project facts.
- Do not start with full AUDIT mode unless explicitly needed.
- Do not let Codex directly fix production logic by default.
- Do not commit `.claude/MEMORY.local.md`.
- Do not overwrite existing project instructions without merge.
