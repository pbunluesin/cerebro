# AI Agent Bootstrap Prompt

Use this prompt when asking Claude, Codex, Gemini, Cursor, or another AI Agent to initialize a new project.

---

You are helping initialize a new software project that will be developed with multiple AI agents.

Follow this core structure:

```text
project-root/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── PROJECT_STATE.md
├── PROCESS.md
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── data-flow.md
│   ├── api-contract.md
│   ├── database-objects.md
│   ├── integration-rules.md
│   ├── security.md
│   ├── testing-strategy.md
│   ├── observability.md
│   ├── deployment-runbook.md
│   ├── troubleshooting.md
│   └── decisions/
│       ├── 0000-adr-template.md
│       └── 0001-agent-workflow.md
└── .claude/
    └── rules/
        ├── sql-server.md
        ├── python.md
        ├── api-review.md
        └── security-review.md
```

Agent roles:

- Human owner is the final decision maker.
- Claude Code is the main implementer and primary fixer.
- Codex is the independent reviewer and should not directly modify production logic unless explicitly requested.
- Gemini may be used for SQL-specific reasoning or prompt generation.
- ChatGPT may be used for architecture, documentation, and decision support.

Rules:

1. Keep `AGENTS.md` and `CLAUDE.md` concise.
2. Put deep project knowledge in `docs/`.
3. Put current status and next actions in `PROJECT_STATE.md`.
4. Put step-by-step AI workflow in `PROCESS.md`.
5. Before changing API logic, read `docs/api-contract.md` and `docs/integration-rules.md`.
6. Before changing SQL/database logic, read `docs/database-objects.md`.
7. Before modifying security/auth/payment logic, read `docs/security.md`.
8. Before changing deployment or environment configuration, read `docs/deployment-runbook.md`.
9. Before changing monitoring/logging behavior, read `docs/observability.md`.
10. Codex should review diffs and produce findings.
11. Claude should apply valid review fixes.
12. Update documentation when decisions, contracts, behavior, or operational procedures change.

Before generating final files, inspect the existing repository and summarize your understanding.
Ask for missing project-specific context only if necessary.

## Review/Fix Bootstrap Addendum

When initializing a new project, include:

- `CODE_REVIEW.md`
- `.claude/agents/codex-reviewer.md`
- `.claude/agents/claude-fixer.md`
- `docs/review-workflow.md`
- `docs/review_findings.md`
- `docs/bugs/`

Before first review, fill in `CODE_REVIEW.md` with project-specific scope, frozen decisions, invariants, and verification commands.
