# Agentic AI Project Context Pack — Final v3

This is the final recommended template for initializing software projects that use multiple AI coding agents.

It is optimized for a workflow where:

- Claude Code is the main implementer and primary fixer.
- Codex is the independent reviewer.
- Human owner is the final decision maker.
- Gemini/ChatGPT/Cursor/GitHub Copilot may assist depending on the project.

## What to copy into a real project

Copy everything inside:

```text
project-root/
```

into the root of your real project.

## What is optional

Use files inside:

```text
optional-extensions/
```

only when the project uses Cursor, GitHub Copilot, reusable prompts, or custom skills.

## Why v3 exists

v2 fixed the most important structure issue: `docs/` is now correctly placed under the actual project root.

v3 improves v2 by adding:

- `docs/README.md` as a documentation index
- `docs/testing-strategy.md`
- `docs/observability.md`
- `docs/troubleshooting.md`
- `docs/decisions/0000-adr-template.md`
- clearer separation between core template, optional extensions, and project-specific examples
- a final `Summary.html`

## What Final v3.2 Adds

Final v3.2 adds a complete review/fix layer:

- `project-root/CODE_REVIEW.md`
- `project-root/.claude/agents/codex-reviewer.md`
- `project-root/.claude/agents/claude-fixer.md`
- `project-root/docs/review-workflow.md`
- `project-root/docs/review_findings.md`
- `project-root/docs/bugs/.gitkeep`
- `project-root/docs/decisions/0003-codex-review-claude-fix.md`
- `optional-extensions/prompts/05-run-codex-review.md`
- `optional-extensions/prompts/06-run-claude-fixer.md`
- `INSTALL_REVIEW_AGENTS_USER_SCOPE.md`
- `ANALYSIS_uploaded_review_files.md`


## Public Repo Usage

If this pack is hosted as a public GitHub repository, read `PUBLIC_REPO_USAGE.md` and `Summary.html` before copying `project-root/` into a new project.


## Markdown File Meaning

Read `MARKDOWN_FILE_MEANING.md` to understand the responsibility of each Markdown file before customizing the template.


## Visible Review Agent Entry Points

`project-root/CODEX-REVIEWER.md` and `project-root/CLAUDE-FIXER.md` are human-readable root entry points. The actual Claude Code subagents live under `project-root/.claude/agents/`.
