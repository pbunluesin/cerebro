# [PROJECT_NAME]

## Purpose

[Describe the business purpose, main users, and the problem this project solves.]

## Technology Stack

- Frontend: [Next.js / React / Other]
- Backend: [Node.js / Python / Other]
- Database: [SQL Server / PostgreSQL / BigQuery / Other]
- Cloud/Hosting: [GCP / AWS / Azure / On-prem / Other]
- Monitoring: [Grafana / Looker / Cloud Logging / Other]

## AI Agent Workflow

This project uses multiple AI agents with separated responsibilities:

| Role | Agent |
|---|---|
| Main implementer / fixer | Claude Code |
| Independent reviewer | Codex |
| Final decision maker | Human owner |
| SQL/prompt helper | Gemini |
| Architecture/docs support | ChatGPT |

Read these files before making changes:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `PROCESS.md`
4. `PROJECT_STATE.md`
5. Relevant files under `docs/`

## Project Documentation

The long-term project knowledge base is in:

```text
docs/
```

Do not rely only on chat history or agent memory.
