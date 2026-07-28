# Generated Document Contracts

## Contents

1. Core rule
2. Root files
3. Durable documents
4. Quality artifacts
5. Update routing
6. Anti-duplication rules

## Core rule

Store each fact in one canonical place. Other files link to it; they do not paraphrase it at length.

## Root files

### `README.md`

Serve humans. Include purpose, quick start, repository map, development commands, testing, and links to deeper docs. Do not encode agent-only behavior.

### `AGENTS.md`

Serve all coding agents. Keep it concise and durable. Include:

- what to read first
- repository-specific commands
- non-negotiable conventions and invariants
- documentation routing
- verification expectations
- No Magic, Verify Before Done, Dissent, and Scope Drift Detection
- R0/R1/R2 behavior and destructive-action constraints
- exact project-root deletion boundary and secret handling
- Claude-implementation, Codex-review, Claude-fix separation

Do not put current tasks or long architecture explanations here.

### `CLAUDE.md`

Serve as a thin Claude-specific adapter. Link to `AGENTS.md`, `PROJECT_STATE.md`, and relevant `.claude/rules/`. Do not duplicate shared rules.

### `PROJECT_STATE.md`

Serve as the current continuation point. Keep:

- current phase and objective
- last verified state
- in-progress and next actions
- current risks and blockers
- recent decision links
- exact validation commands
- a compact operational handoff block when pausing, following the installed `handoff` skill's contract

Remove completed narration that Git history or durable docs already preserve. Never turn this into a process manual.

### `.cerebro/project.json`

Serve as the canonical generated-project contract. Record:

- generator/plugin version and generation date;
- project identity;
- selected scaffold profile and agent adapters;
- optional features and stack-specific scaffold assets;
- the exact canonical required-file plan; and
- the path and SHA-256 of `.cerebro/stack-profile.json`.

Keep it versioned with the project. Do not hand-edit it to bypass validation.
Regenerate it through `bootstrap_project.py` when the scaffold contract changes.
Final validation derives expected artifacts from this manifest; caller flags
are assertions, not alternative sources of truth.

### `.cerebro/stack-profile.json`

Serve as the generated, machine-readable record of:

- exact runtime, framework, database versions, and path scopes;
- approved official scaffold, documentation, and example references;
- Stack Pack versions and content hashes;
- selected Good/Bad rule IDs and explicit exceptions;
- the human approval checkpoint for reference selection.

Keep it versioned with the project. Do not hand-edit selected rules or copy the
complete Cerebro packs into the project. Regenerate it through
`select_stack_rules.py` after an approved version, path, or pack change.
Approval records use
`requirements-final:<YYYY-MM-DD>:<approver>`. Paths must be normalized,
project-relative globs and resolved refs must match the selected stack/version's
catalog format.

### `.env.example`

List safe variable names and non-secret examples. Document ownership and purpose. Never include live credentials, production hosts with embedded authentication, private keys, or copied secret values.

## Durable documents

### `docs/PRODUCT.md`

Own the problem, users, desired outcomes, success signals, scope, non-goals, and first-release boundary.

### `docs/REQUIREMENTS.md`

Own numbered functional and non-functional requirements, business rules, scenarios, acceptance criteria, traceability, assumptions, and deferred scope.

### `docs/CONTEXT.md`

Own canonical domain terms and rejected ambiguous alternatives. Do not use it as a spec or scratchpad.

### `docs/CONTEXT_MAP.md` and `docs/contexts/*.md`

Create these lazily only when multiple real bounded contexts have different language or ownership. `CONTEXT.md` retains only project-wide terms, the map owns context relationships, and each context file owns its own canonical terms. Do not infer contexts from folder, team, deployable, or database boundaries alone.

### `docs/ARCHITECTURE.md`

Own system boundary, modules, complete caller-visible interfaces, dependencies, justified seams/adapters, flows, trust boundaries, failure handling, and architecture risks. Link to contracts and ADRs.

### `docs/DATA.md`

Own sources of truth, entities, identifiers, relationships, integrity rules, classification, retention, reconciliation, migration constraints, and recovery.

### `docs/API.md`

Own interface contracts, authentication, versioning, idempotency, timeouts, retries, rate limits, error shapes, compatibility, and contract validation.

### `docs/SECURITY.md`

Own assets, actors, trust boundaries, threats, authorization rules, secrets, privacy, logging restrictions, dependency risk, and security validation.

### `docs/TESTING.md`

Own test layers, commands, fixtures, coverage priorities, acceptance mapping, manual checks, and definition of done.

### `docs/OPERATIONS.md`

Own environments, deployment, configuration, observability, alerting, ownership, rollback, disaster recovery, runbooks, and post-deployment verification.

### `docs/MIGRATION.md`

Own source/target states, compatibility window, data transformation, dry run, backfill, cutover, rollback, reconciliation, and completion evidence.

### `docs/decisions/*.md`

Record only decisions that pass the `domain-modeling` decision gate. Keep the template until the first decision is created; do not treat the template as an accepted decision.

## Quality artifacts

### `docs/quality/REVIEW_CONTRACT.md`

Own review scope, frozen decisions, invariants, verification commands, severity, evidence standard, and finding format. Populate it with real project commands before using automated review.

### `docs/quality/findings/`

Store one evidence-backed file per confirmed finding. Track status explicitly. Do not file speculative style preferences as defects.

### `docs/quality/THREAT_MODEL.md`

For critical projects, record protected assets, actors, entry points, trust boundaries, abuse cases, mitigations, residual risk, and validation.

### `docs/quality/RELEASE_CHECKLIST.md`

For critical projects, record pre-deploy evidence, approvals, migration and rollback checks, observability checks, and post-deploy verification.

## Update routing

| Change | Update |
|---|---|
| Goal, user, scope, success signal | `PRODUCT.md`, then state link |
| Behavior or acceptance | `REQUIREMENTS.md` |
| Domain terminology | `CONTEXT.md`, or the owning file under `contexts/` |
| Bounded-context ownership/relationship | `CONTEXT_MAP.md` and affected context files |
| Module, boundary, or flow | `ARCHITECTURE.md` and possibly ADR |
| Data semantics | `DATA.md`, tests, and possibly ADR |
| Interface contract | `API.md`, contract tests, review contract |
| Security or privacy behavior | `SECURITY.md`, threat model, tests |
| Deployment, monitoring, recovery | `OPERATIONS.md` |
| Stack version, approved reference, rule, or path scope | `.cerebro/stack-profile.json`, then affected architecture/tests |
| SQL Server procedure team policy | Installed `sqlserver-house-standard.md`; project profile stores DBHS-01 version/hash and procedure object files implement it |
| SQL Server function/trigger/type team policy | Installed `sqlserver-object-house-standard.md`; project profile stores DBHS-02 version/hash and applicable object files implement it |
| SQL Server design/normalization/index/optimization guidance | Installed `sqlserver-engineering-practices.md`; project profile stores DBEP-01 version/hash and project-specific decisions/evidence stay in `DATA.md`, architecture, ADRs, migrations, tests, or operations as appropriate |
| Current work only | `PROJECT_STATE.md` |
| Durable agent rule | `AGENTS.md` or closest nested `AGENTS.md` |
| Repeatable workflow | Cerebro skill, not generated project docs |

## Anti-duplication rules

- Do not create `PROCESS.md`.
- Do not create both `docs/adr/` and `docs/decisions/`; use `docs/decisions/`.
- Do not create separate Codex and Claude copies of requirements or architecture.
- Do not duplicate `AGENTS.md` rules in `CLAUDE.md`.
- Do not copy issue history into `PROJECT_STATE.md` when findings or Git already preserve it.
- Do not copy the full SQL Server house standard into project docs or
  `AGENTS.md`; keep only selected rule IDs/profile metadata and project-specific
  exceptions.
- Do not keep empty documents merely because a template created them.
