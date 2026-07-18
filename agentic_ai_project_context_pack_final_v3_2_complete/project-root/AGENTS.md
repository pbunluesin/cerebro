# AGENTS.md

Shared instructions for AI agents working in this repository.

## Principle

Do not assume project context. Read the relevant documentation before modifying code.

## Agent Roles

| Agent | Primary Role | Default Permission |
|---|---|---|
| Claude Code | Main implementer and fixer | May modify code |
| Codex | Reviewer / second opinion | Review first, patch only if explicitly requested |
| Gemini | SQL/prompt helper | Advisory |
| ChatGPT | Architecture/documentation/decision support | Advisory |
| Human Owner | Final decision maker | Approves important decisions |

## Required Reading

Before starting:

1. Read `PROJECT_STATE.md`
2. Read `PROCESS.md`
3. Read relevant files under `docs/`

Task-specific routing:

| Task Type | Required Docs |
|---|---|
| Architecture change | `docs/architecture.md` |
| Data flow change | `docs/data-flow.md` |
| API change | `docs/api-contract.md`, `docs/integration-rules.md` |
| Database/SQL change | `docs/database-objects.md`, `docs/data-flow.md` |
| Auth/security/payment change | `docs/security.md` |
| Test strategy change | `docs/testing-strategy.md` |
| Logging/monitoring change | `docs/observability.md` |
| Deployment change | `docs/deployment-runbook.md` |
| Incident/debugging | `docs/troubleshooting.md` |

## Review Rules

- Review the diff, not only the final file.
- Separate findings by severity: Critical, High, Medium, Low.
- Focus on correctness, security, data integrity, maintainability, and business-rule preservation.
- Do not rewrite large sections without explaining why.
- Do not change API contracts without checking `docs/api-contract.md`.
- Do not change database semantics without checking `docs/database-objects.md`.

## Documentation Rules

Update documentation when:

- API contract changes
- Database schema, view, or stored procedure changes
- Business rule changes
- Security/auth/payment behavior changes
- Deployment process changes
- Monitoring/logging behavior changes
- A major architecture decision is made

## Review / Fix Layer

This project uses a formal review/fix loop:

- `CODE_REVIEW.md` is the review brief and single source of truth.
- `.claude/agents/codex-reviewer.md` performs review through Codex and writes review artifacts only.
- `.claude/agents/claude-fixer.md` fixes one OPEN bug at a time and never calls Codex.
- `docs/review-workflow.md` explains invocation and workflow.
- `docs/bugs/*.md` and `docs/review_findings.md` are durable review artifacts.

Do not bypass `CODE_REVIEW.md` for review/fix work.

## Operating Guardrails

All agents must follow `docs/guardrails.md`.

- NO MAGIC: do not invent paths, services, endpoints, env vars, database objects, or business rules.
- VERIFY BEFORE DONE: do not claim completion without evidence.
- DISSENT: challenge major changes before implementation.
- SCOPE DRIFT: stop and flag when a small task expands into a refactor/redesign.
- R0/R1/R2: classify meaningful changes by reversibility.
