# docs/

This folder is the long-term project knowledge base.

AI agents should not read every document for every task.
Use this index to route agents to the right file.

## Documentation Index

| File | Purpose |
|---|---|
| `architecture.md` | System architecture and component responsibilities |
| `data-flow.md` | How data moves through the system |
| `api-contract.md` | Endpoints, request/response, auth, error behavior |
| `database-objects.md` | Tables, views, stored procedures, indexes |
| `integration-rules.md` | Vendor/system mapping and integration behavior |
| `security.md` | Auth, secrets, payment, PII, sensitive behavior |
| `testing-strategy.md` | Unit, integration, E2E, dry-run, regression testing |
| `observability.md` | Logs, metrics, dashboards, alerts |
| `deployment-runbook.md` | Deploy, rollback, environment setup |
| `troubleshooting.md` | Known failures and debugging flow |
| `decisions/` | Architecture Decision Records |

## Rule

If a behavior changes, update the relevant document.

| `guardrails.md` | AI operating guardrails: no guessing, verify-before-done, scope drift, R0/R1/R2 |
| `review-workflow.md` | Codex review and Claude fix workflow |
| `review_findings.md` | Review findings index and priority tracker |
| `bugs/` | One markdown file per confirmed BUG finding |