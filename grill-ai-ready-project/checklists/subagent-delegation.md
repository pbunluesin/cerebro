# Subagent Delegation Checklist

Use this checklist when `grill-ai-ready-project` is run in a repo that supports Claude Code subagents.

## Delegation Routing

- Use `codebase-cartographer` before asking questions in an existing repo.
- Use `project-griller` when requirements, scope, users, or business rules are vague.
- Use `docs-architect` when creating or auditing `CLAUDE.md`, `docs/PROJECT_STATE.md`, `docs/PROCESS.md`, `docs/CONTEXT.md`, or ADRs.
- Use `api-contract-reviewer` for APIs, webhooks, callbacks, vendor integrations, request/response contracts, and auth headers.
- Use `data-model-reviewer` for database schema, migrations, source-of-truth, sync, ETL/ELT, SQL Server, or BigQuery work.
- Use `security-reviewer` for auth, permissions, PII, payment, secrets, service accounts, logging, or production configuration.
- Use `deployment-reviewer` for Cloud Run, App Engine, GCP, CI/CD, environment variables, rollback, and observability.
- Use `implementation-readiness-reviewer` after grilling and docs updates to produce the final readiness status.

## Required Aggregation

The main Claude session remains responsible for final decisions and must aggregate subagent outputs into:

- `docs/PROJECT_STATE.md`
- `docs/REQUIREMENTS.md`
- `docs/CONTEXT.md`
- `docs/PROCESS.md`
- `docs/adr/*.md` when justified
- final readiness summary

## Guardrails

- Do not create subagents that auto-deploy, auto-delete, or auto-run destructive commands.
- Do not delegate secrets inspection.
- Do not mark implementation as ready based on one subagent only.
- If subagents disagree, summarize the conflict and ask the user only if it blocks implementation.
