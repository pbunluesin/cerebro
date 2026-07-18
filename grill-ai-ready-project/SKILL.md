---
name: grill-ai-ready-project
description: Stress-test a project idea or change against existing docs/code, resolve requirements one question at a time, sharpen shared language, record important decisions, and generate an AI-ready project documentation structure before implementation. Use when starting a new project, onboarding Claude Code into an existing repo, preparing a feature for implementation, or converting vague requirements into project-standard Markdown files.
argument-hint: "[project idea / change request / repo goal] [--grill-only|--docs-only|--audit-existing|--production|--small|--codex-plan-review|--codex-review-only|--mcp-first|--codex-cli|--manual-codex]"
---

# Grill AI-Ready Project

Version: 1.3

## Purpose

Use this skill to turn a rough project idea, feature request, vendor integration, migration plan, or existing repository into an **AI-ready engineering project**.

The workflow combines:

- requirement grilling
- docs-aware codebase exploration
- shared language / glossary refinement
- minimal ADR creation only when justified
- architecture and implementation readiness checks
- AI-agent handoff preparation
- project-standard Markdown generation
- optional cross-model Codex plan review before implementation
- optional Codex code-review coordination after implementation

The goal is to prevent vague requirements from becoming fragile implementation work while preserving the core behavior of `grill-me` and `grill-with-docs`.

## Inspiration and Attribution

This skill is an original adaptation inspired by Matt Pocock's `grill-me` and `grill-with-docs` skills from `mattpocock/skills`, which use a grilling session to resolve uncertainty, ask one question at a time, explore the codebase when possible, sharpen terminology, update context docs, and create ADRs only when justified.

Version 1.3 also adapts the cross-model plan-hardening idea from `chaseai-yt/grill-me-codex`: Claude prepares a locked plan, an independent Codex reviewer attacks the plan in read-only mode, Claude revises with logged reasoning, and the user gives final sign-off before code. This package is MCP-first for users who already call Codex from Claude Code via MCP, while keeping Codex CLI and manual-prompt fallbacks.

This package includes attribution in `LICENSE-ATTRIBUTION.md`. Do not remove that file if distributing this skill or a substantial derivative.


## Upstream Compatibility Layer

Preserve these core behaviors from the upstream skills:

### From `grill-me`

- Interview relentlessly until shared understanding is reached.
- Walk down the design tree branch by branch.
- Resolve dependencies between decisions one by one.
- For each question, provide a recommended answer when possible.
- Ask one question at a time and wait for feedback before continuing.
- If the answer can be found by exploring the codebase, inspect the codebase instead of asking the user.

### From `grill-with-docs`

- Challenge the plan against the existing domain model and documented decisions.
- Look for `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs before asking questions.
- Call out conflicts between user language and existing glossary terms immediately.
- Sharpen vague or overloaded terminology into canonical terms.
- Discuss concrete scenarios and edge cases to expose boundary problems.
- Cross-reference user claims with the actual code and docs.
- Update `CONTEXT.md` inline as terms are resolved.
- Keep `CONTEXT.md` as a glossary only, not a spec, scratchpad, or implementation plan.
- Offer ADRs sparingly and only when the decision is hard to reverse, surprising without context, and the result of a real trade-off.

This skill adds an AI-ready project documentation layer on top of those behaviors; it does not replace the original upstream skills.

## Modes

Parse `$ARGUMENTS` for these optional modes:

- `--grill-only`: ask questions and resolve requirements; do not write files unless explicitly requested.
- `--docs-only`: generate/update Markdown files from already-known context; ask only if blocked.
- `--audit-existing`: inspect current docs and report gaps against this standard.
- `--production`: include full production docs, security, deployment, rollback, data, API, ADR, and testing requirements.
- `--small`: use a lightweight documentation set for small/internal tools.
- `--codex-plan-review`: after grilling/docs, create `PLAN.md` and run/coordinate an independent Codex adversarial review before implementation.
- `--codex-review-only`: skip grilling and docs generation; review an existing `PLAN.md` with Codex before code.
- `--mcp-first`: prefer the user's configured Claude Code MCP tool/server that calls Codex.
- `--codex-cli`: use local Codex CLI commands as the fallback review path.
- `--manual-codex`: generate a copy/paste prompt for Codex when no MCP/CLI integration is available.

Default mode: grill first, then create/update docs when the requirement is sufficiently clear. Codex review is optional unless the user asks for it or the work is high-risk and the user agrees.

## Core Operating Rules

1. Ask **one question at a time** during grilling.
2. For each question, include a recommended answer when a good default is possible.
3. If the answer can be found by reading the repo, docs, or code, inspect first instead of asking.
4. Do not implement application code in this skill unless the user explicitly asks.
5. Do not overwrite important existing files blindly. Read first, then merge or improve.
6. Use `TBD` for unknowns instead of inventing facts.
7. Keep `CLAUDE.md` concise and make it an index to deeper docs.
8. Keep `CONTEXT.md` as a glossary/shared language document, not a spec or scratchpad.
9. Create ADRs sparingly, only for decisions that are hard to reverse, surprising without context, and the result of a real trade-off.
10. Treat secrets, credentials, production keys, service account JSON, and private certificates as protected. Never copy them into docs.
11. Before implementation readiness is marked `Ready`, confirm that acceptance criteria and validation steps exist.
12. If the user says to proceed and something is only mildly uncertain, use a safe default and record it as an assumption.
13. For high-risk work such as payments, auth, schema changes, migrations, concurrency, callbacks/webhooks, or production deployment, recommend Codex plan review before implementation.
14. Keep Codex independent: provide it direct artifacts (`PLAN.md`, relevant docs, repo paths, diffs, test output), not only Claude's summary.
15. Codex review must be read-only. Codex advises; Claude remains the orchestrator and must log accepted/rejected critiques with reasons.

## Phase 0 — Optional Subagent Delegation Layer

When Claude Code subagents are available, use them to keep the main conversation focused and to reduce context pollution. The main Claude session remains the owner of final decisions, user-facing questions, and final documentation.

This skill package includes project-level subagent templates in:

```txt
templates/.claude/agents/
```

When bootstrapping a production project, create or update these project-level subagents if the user wants the repo to include agent definitions:

```txt
.claude/agents/codebase-cartographer.md
.claude/agents/project-griller.md
.claude/agents/docs-architect.md
.claude/agents/api-contract-reviewer.md
.claude/agents/data-model-reviewer.md
.claude/agents/security-reviewer.md
.claude/agents/deployment-reviewer.md
.claude/agents/implementation-readiness-reviewer.md
.claude/agents/codex-review-coordinator.md
```

### Delegation Routing

- Use `codebase-cartographer` first for existing repositories to map tech stack, docs, tests, deployment files, and likely impact areas.
- Use `project-griller` when scope, business rules, or acceptance criteria are unclear.
- Use `docs-architect` when creating or auditing AI-ready docs, `CONTEXT.md`, `PROJECT_STATE.md`, `PROCESS.md`, and ADRs.
- Use `api-contract-reviewer` when APIs, webhooks, callbacks, vendor contracts, auth headers, or payload schemas are involved.
- Use `data-model-reviewer` when databases, migrations, ETL/ELT, source-of-truth, SQL Server, BigQuery, or data sync are involved.
- Use `security-reviewer` when auth, permissions, PII, secrets, payment, service accounts, or production configuration are involved.
- Use `deployment-reviewer` when CI/CD, GCP, Cloud Run, App Engine, environment variables, rollback, monitoring, or production operations are involved.
- Use `implementation-readiness-reviewer` as the final gate before coding.
- Use `codex-review-coordinator` when `--codex-plan-review`, `--codex-review-only`, MCP Codex, Codex CLI, or manual Codex review is requested.

### Delegation Rules

1. Do not delegate direct user interaction unless the main session controls the final question.
2. Do not mark a project `Ready` based on a single subagent result.
3. Aggregate subagent findings into the docs; do not leave findings only in transient conversation.
4. If subagents disagree, summarize the conflict and resolve it with evidence from code/docs or ask the user only if it blocks implementation.
5. Never use subagents to inspect or copy secrets, credentials, private keys, service account JSON, or production tokens.
6. Do not use subagents to auto-deploy, auto-delete, or run destructive commands.

If subagents are not available, run the same review roles sequentially in the main session using the checklists in `checklists/`.


## Phase 0.5 — Optional Codex Adversarial Review Layer

Use this layer when the user wants a second-model sanity check, or when the work is high-risk: payment platforms, authentication, authorization, database schema, migrations, callbacks/webhooks, reconciliation, concurrency, security-sensitive logging, production deployment, or vendor/API contracts.

### Roles

- Claude = planner, implementer, orchestrator, and final summarizer.
- Codex = independent read-only adversarial reviewer.
- Subagents = specialist reviewers inside Claude Code.
- User = final decision maker and implementation gate.

### MCP-First Strategy

If the user has a Codex MCP integration inside Claude Code, prefer it over shelling out to Codex CLI. The skill should:

1. Detect/ask which Codex review path is available: MCP, Codex CLI, or manual prompt.
2. Prefer `--mcp-first` when the MCP tool is configured.
3. Send Codex the actual artifacts: `PLAN.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/API_SPEC.md`, `docs/DATA_MODEL.md`, relevant repo files, and later `git diff`/test output.
4. Ask Codex for `VERDICT: APPROVED` or `VERDICT: REVISE`.
5. Write every round into `PLAN-REVIEW-LOG.md`.
6. If Codex asks for revisions, Claude decides what to accept or reject and logs why.
7. Stop at `MAX_ROUNDS` and surface deadlocks instead of pretending the plan converged.
8. Never write code until the user signs off after Codex review.

### Review Artifacts

Use these files when Codex review is enabled:

```txt
PLAN.md
PLAN-REVIEW-LOG.md
docs/CODEX_REVIEW.md                 # optional summary for completed reviews
docs/IMPLEMENTATION_REVIEW_LOG.md    # optional after code review
```

### Tunables

```txt
MAX_ROUNDS=5
PLAN_FILE=PLAN.md
LOG_FILE=PLAN-REVIEW-LOG.md
CODEX_REVIEW_MODE=mcp-first | codex-cli | manual-codex
```

### Codex Review Prompt Contract

Codex should be instructed as an independent adversarial reviewer:

```txt
You are reviewing an implementation plan as an independent adversarial reviewer.
Be skeptical and specific. Do not assume Claude's plan is correct.
Read PLAN.md and relevant project docs/code directly.
Find material flaws: missing requirements, security issues, race conditions,
schema conflicts, callback/webhook risks, idempotency gaps, reconciliation gaps,
observability gaps, deployment/rollback gaps, and simpler safer alternatives.
For every issue, give a concrete fix.
Do not modify files.
End with exactly one line:
VERDICT: APPROVED
or
VERDICT: REVISE
```

### CLI Fallback Safety

If using Codex CLI instead of MCP, use read-only mode and avoid stdin hangs:

```bash
codex exec -s read-only --json -o /tmp/codex-verdict.txt "$(cat REVIEW_PROMPT)" < /dev/null
```

For resumed rounds, force read-only explicitly because resume may not accept the same sandbox flag:

```bash
codex exec resume "$THREAD_ID" -c sandbox_mode="read-only" --json   -o /tmp/codex-verdict.txt   "I revised PLAN.md. Re-review only material issues. End with VERDICT: APPROVED or VERDICT: REVISE."   < /dev/null
```

### Code Review Boundary

Plan review and code review are separate.

- Before code: use `PLAN.md` + `PLAN-REVIEW-LOG.md`.
- After code: use Codex/MCP code review against `git diff`, changed files, test output, and relevant docs.
- Do not let the plan-review loop become a code-writing loop.

## Phase 1 — Discover Existing Context

Before asking questions or writing docs, inspect the repository when available:

- existing `CLAUDE.md`
- existing `README.md`
- existing `CONTEXT.md` or `CONTEXT-MAP.md`
- existing `docs/`
- existing ADR directory: `docs/adr/`, `docs/ADR/`, or `docs/decisions/`
- package/build files such as `package.json`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, `app.yaml`, `cloudbuild.yaml`, `.github/workflows/*`
- database/migration folders
- API/openapi files
- test folders
- deployment/config folders

Then summarize what is known and what is missing.

## Phase 2 — Grill the Requirement

Ask focused questions until the project/change has enough clarity to produce useful docs.

Question categories:

1. Goal and business outcome
2. Users and stakeholders
3. Scope and out-of-scope
4. Current system behavior
5. Desired behavior
6. Data ownership and source of truth
7. API/integration contracts
8. Authentication and authorization
9. Security and privacy
10. Error handling and retry strategy
11. Observability and auditability
12. Testing and acceptance criteria
13. Deployment and rollback
14. Migration/backfill/compatibility
15. Open risks and trade-offs

During grilling:

- challenge vague terms immediately
- propose canonical terms for overloaded language
- test edge cases with concrete scenarios
- identify decisions that block implementation
- separate business decisions from technical decisions
- keep a running list of assumptions and open questions

## Phase 3 — Shared Language

Create or update `docs/CONTEXT.md` when project terms become clear.

Rules for `CONTEXT.md`:

- glossary/shared language only
- no implementation details
- no temporary notes
- no requirements dumping
- no general programming concepts unless they are domain-specific in this project
- be opinionated: pick one canonical term and list alternatives under `_Avoid_`
- keep definitions tight, usually one or two sentences
- group terms under subheadings only when natural clusters emerge

Single-context repos normally use one root `CONTEXT.md`. Multi-context repos may use `CONTEXT-MAP.md` to point to context-specific `CONTEXT.md` files. If `CONTEXT-MAP.md` exists, read it first and infer the relevant context. If unclear, ask.

Use this default format:

```md
# <Context Name>

<One or two sentence description of what this context is and why it exists.>

## Language

**<Canonical Term>**: <one or two sentence definition>
_Avoid_: <ambiguous or rejected terms>
```

## Phase 4 — Decision Capture

Create an ADR only when all are true:

1. The decision is hard or costly to reverse.
2. A future engineer/agent would ask why this path was chosen.
3. There were real alternatives and trade-offs.

ADR location:

- follow the repo's existing ADR convention if one exists
- otherwise prefer upstream-compatible `docs/adr/0001-<slug>.md`
- create the ADR directory lazily only when the first ADR is needed

ADR format:

- prefer a short ADR first: title plus 1-3 sentences explaining the context, decision, and why
- include optional sections such as Status, Considered Options, Consequences, and Follow-up actions only when they add genuine value
- do not create heavyweight ADRs for obvious or easy-to-reverse decisions

## Phase 5 — Materialize Docs

When enough context is resolved, create or update the AI-ready documentation set.

### Small Project Mode

Use for small scripts, prototypes, internal tools, and low-risk apps:

```txt
CLAUDE.md
README.md
CHANGELOG.md
docs/PROJECT_STATE.md
docs/REQUIREMENTS.md
docs/PROCESS.md
docs/CONTEXT.md
```

### Production Project Mode

Use for production apps, payment systems, SSO, vendor APIs, data sync, database work, GCP/cloud systems, internal enterprise apps, and systems with security or operational risk:

```txt
CLAUDE.md
README.md
CHANGELOG.md
.env.example
docs/PROJECT_OVERVIEW.md
docs/PROJECT_STATE.md
docs/REQUIREMENTS.md
docs/CONTEXT.md
docs/ARCHITECTURE.md
docs/DATA_MODEL.md
docs/API_SPEC.md
docs/DEVELOPMENT.md
docs/TESTING.md
docs/DEPLOYMENT.md
docs/SECURITY.md
docs/TROUBLESHOOTING.md
docs/PROCESS.md
docs/adr/0001-initial-project-standard.md
PLAN.md                    # only when plan review is enabled
PLAN-REVIEW-LOG.md         # only when Codex/adversarial review is enabled
docs/CODEX_REVIEW.md       # optional summary
docs/IMPLEMENTATION_REVIEW_LOG.md # optional after code review
.claude/settings.example.json
.claude/agents/*.md
```

## File Responsibilities

- `CLAUDE.md`: concise AI instruction and doc index
- `README.md`: human quick start
- `CHANGELOG.md`: notable changes and release history
- `.env.example`: safe env variable template
- `docs/PROJECT_OVERVIEW.md`: business and technical overview
- `docs/PROJECT_STATE.md`: current AI working memory and continuation point
- `docs/REQUIREMENTS.md`: requirements, acceptance criteria, scope boundaries
- `docs/CONTEXT.md`: shared domain language only
- `docs/ARCHITECTURE.md`: architecture, modules, flows, integration points
- `docs/DATA_MODEL.md`: tables/entities, ownership, keys, data quality rules
- `docs/API_SPEC.md`: endpoint contracts and integration behavior
- `docs/DEVELOPMENT.md`: local development guide
- `docs/TESTING.md`: validation, regression, test commands
- `docs/DEPLOYMENT.md`: deployment and rollback steps
- `docs/SECURITY.md`: security, auth, PII, secret handling
- `docs/TROUBLESHOOTING.md`: known errors and fixes
- `docs/PROCESS.md`: AI-assisted engineering workflow
- `docs/adr/*.md`: architectural decisions

## Implementation Readiness Gate

Before saying the project is ready for implementation, produce this status:

```md
## Implementation Readiness

Status: Ready | Partially Ready | Not Ready

Ready because:
- ...

Blocking gaps:
- ...

Safe assumptions:
- ...

Required before coding:
- ...

Validation path:
- ...
```

Only mark `Ready` when:

- goal is clear
- scope is clear
- acceptance criteria exist
- impacted modules are known or discoverable
- validation steps are defined
- security considerations are captured
- rollback/deployment notes exist for production changes

## AI Agent Handoff Standard

Add this section to `docs/PROJECT_STATE.md` when useful:

```md
## AI Agent Handoff

Current objective:

Files to read first:

Files likely to change:

Do not touch:

Important decisions:

Validation commands:

Expected outcome:

Open questions:
```

## Default First Response

When invoked, respond with a concise plan and then begin with the first high-impact question unless `--docs-only` or `--audit-existing` was supplied.

Example first question:

> Before we generate docs, what is the main business outcome this project must achieve? My recommended default is to define this in one sentence as: "This project exists to [do X] for [user/stakeholder] so that [measurable outcome]."

## Final Response Requirements

At the end, summarize:

- files created
- files updated
- docs intentionally skipped
- assumptions recorded
- open questions
- subagents created/updated, if any
- implementation readiness status
- Codex review mode/result, if used
- recommended next command/workflow

Do not claim production readiness unless the production docs, security notes, validation path, and rollback notes are present.
