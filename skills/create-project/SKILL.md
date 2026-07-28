---
name: create-project
description: Turn a vague software idea into validated final requirements, approved current official implementation references, version/path-scoped Good/Bad rules, and a right-sized AI-ready project structure for Codex and Claude. Use when a user wants to start, bootstrap, architect, or “grill” a new project; asks for requirements discovery before coding; wants a best-practice Markdown/documentation tree; or needs default agent guidance, guardrails, review rules, and optional development-tool setup. Continue interviewing one decision at a time until the implementation-readiness gate passes, then scaffold and validate the project. Do not use to retrofit a mature repository; use audit-project instead.
---

# Create Project

Transform an idea into an implementation-ready project without inventing missing requirements or generating code prematurely.

## Operating contract

- Read [safety-contract.md](references/safety-contract.md) in full before any mutation, tool installation, major decision, or commit-related handoff.
- Inspect before asking. Resolve facts from supplied context, existing files, or authorized sources.
- Ask one question at a time. Select the unresolved question with the highest downstream impact.
- Give a recommended answer and its trade-off whenever evidence supports one.
- Challenge vague words with concrete scenarios, boundaries, and failure cases.
- Maintain a canonical domain-language ledger; never let two meanings hide behind one term.
- Separate confirmed facts, user decisions, safe assumptions, and open questions.
- Do not declare readiness while any blocking question remains.
- Do not write application code. End with a validated project structure and an actionable first vertical slice unless the user separately requests implementation.
- Never install software, execute remote installers, or change user-global configuration without explicit approval.
- Treat the explicit target directory as `WORK_ROOT`. Never delete, move, overwrite, or recursively mutate a path outside it without exact per-action approval.

## Parse the request

Accept natural-language instructions plus these optional controls:

- `--target <path>`: project directory to create or populate.
- `--profile minimal|standard|critical`: override automatic profile selection.
- `--agents codex|claude|both`: default to `both`.
- `--stacks <comma-separated-scaffold-scopes>`: normally derived from the
  approved stack profile; currently `sqlserver` adds the team procedure,
  function, trigger, type, and data-document assets.
- `--requirements-only`: stop after the final requirements package.
- `--prototype`: allow a deliberately disposable prototype path; record omitted readiness work.
- `--non-interactive`: use safe assumptions for non-blocking gaps, but stop on blocking product, security, data, or operational decisions.

Do not infer an unsafe target path. Require an explicit path before materializing files.

## Stage 1: Discover evidence

1. Determine whether the target is empty, new, or already contains a project.
2. If it contains a mature project, invoke or recommend `audit-project`; do not overwrite it with a new-project template.
3. Inspect any supplied brief, conversation context, prototypes, diagrams, contracts, repositories, and stakeholder notes.
4. Summarize only:
   - confirmed facts
   - likely constraints supported by evidence
   - contradictions
   - missing decisions
5. Initialize an interview ledger in the conversation with these states:
   - `CONFIRMED`
   - `DECIDED`
   - `ASSUMED`
   - `OPEN-BLOCKING`
   - `OPEN-NONBLOCKING`

Before interviewing, read [requirements-gate.md](references/requirements-gate.md) in full. Use its routing matrix rather than asking every possible question.

When project-specific language, ownership, lifecycle, or bounded contexts are material, read [domain-modeling](../domain-modeling/SKILL.md) in full. Apply its ambiguity and scenario probes during the interview. Before the target is materialized, keep confirmed terms in the interview ledger; after materialization, write them to the canonical context documents without reinterpretation.

## Stage 2: Grill one decision at a time

Repeat this loop:

1. Re-rank unresolved decisions by blast radius and dependency count.
2. Inspect available evidence for the top decision.
3. If unresolved, ask exactly one focused question.
4. Include:
   - why the answer matters now
   - a recommended default
   - at most three concrete options when options help
   - the primary trade-off
5. Record the answer in the ledger and propagate its consequences.
6. Expose contradictions immediately.
7. Test the emerging requirement against at least one happy path, one failure path, one boundary case, and one recovery path.
8. When a domain term becomes precise, record its canonical meaning and rejected synonyms immediately in the ledger; do not wait until final synthesis to rediscover it.

Do not ask users to choose implementation trivia that can safely be decided later. Do ask about product behavior, data ownership, trust boundaries, destructive operations, money, identity, compliance, availability, and irreversible constraints.

## Stage 3: Produce the final requirement set

When the requirements gate has no blocking gaps, produce a reviewable final package containing:

- one-sentence outcome
- users and stakeholders
- measurable success signals
- in-scope and out-of-scope boundaries
- user journeys and failure/recovery behavior
- numbered functional requirements (`FR-###`)
- numbered non-functional requirements (`NFR-###`)
- numbered acceptance criteria (`AC-###`)
- business rules and canonical terms
- bounded contexts, ownership, and cross-context language when more than one domain context is real
- data ownership, retention, migration, and privacy constraints when applicable
- interfaces and integrations when applicable
- roles, authentication, and authorization when applicable
- environments, deployment, rollback, observability, and support expectations
- decision ledger, assumptions, risks, and remaining non-blocking questions
- traceability from each requirement to one or more acceptance criteria

Ask the user to confirm this package when their approval would materially change scope. If the user already authorized autonomous progress and no blocking decision remains, record that basis and continue.

Declare `REQUIREMENTS_READY` only after this package is confirmed and its
blocking questions are closed. Do not choose architecture or a scaffold merely
because the requirements document now exists.

## Stage 4: Resolve official references and versioned Stack Packs

Read [reference-selection.md](references/reference-selection.md) in full. This
stage is mandatory unless `--requirements-only` is set.

1. Resolve each runtime, framework, language, database, CSS tool, and deployable
   path to an exact version or an explicit legacy constraint. Do not infer a
   version from syntax, habit, or a default branch.
2. Start from [official-sources.json](references/official-sources.json), then
   verify current official release/support evidence when network use is
   authorized. Treat default branches, preview releases, and community
   boilerplates as candidates—not authority.
3. Select at most four references per deployable: official scaffold, the
   smallest relevant official example, official docs, then an approved house
   standard when one exists. Record exact versions/tags/commits and why each
   reference fits the confirmed requirement.
4. Surface source age, version conflicts, platform constraints, and any
   architecture imported by a scaffold. Obtain and record approval for the
   candidate reference set when it materially constrains the project.
5. Reach `REFERENCE_APPROVED` before architecture or materialization. If the
   source catalog or version policy is stale, exact versions are missing, path
   scope is ambiguous, or a requested version is outside the approved range,
   stop this gate and read
   [update-stack-packs.md](references/update-stack-packs.md); never select a
   nearby rule.
6. Generate only the applicable rules with the dependency-free selector:

   ```bash
   python3 scripts/select_stack_rules.py \
     --stack <scope>@<exact-version> \
     --path '<scope>=<project-relative-glob>' \
     --source-ref '<catalog-scope>=<exact-package-tag-commit-or-dated-docs-ref>' \
     --approval-record 'requirements-final:<YYYY-MM-DD>:<approver>' \
     --out <working-stack-profile.json>
   ```

   Repeat `--stack` for versioned included scopes such as TypeScript, React, or
   accessibility. A framework path propagates to its included scopes; independent
   deployables need independent `--path` values.

The generated profile is the project-facing source. Do not copy the complete
[best-practices.md](references/stack-packs/best-practices.md) or
[anti-patterns.md](references/stack-packs/anti-patterns.md) into a project.
When SQL Server is selected, read every applicable local reference in full:
[sqlserver-house-standard.md](references/stack-packs/sqlserver-house-standard.md)
for procedures,
[sqlserver-object-house-standard.md](references/stack-packs/sqlserver-object-house-standard.md)
for functions/triggers/types, and
[sqlserver-engineering-practices.md](references/stack-packs/sqlserver-engineering-practices.md)
for design/normalization/index/optimization review. Record every applicable
version/hash through the generated profile. Treat DBHS-01 and DBHS-02 as
mandatory user team policy, and DBEP-01 as Microsoft-derived guidance whose
context-sensitive decisions still require exact target and workload evidence.
Do not infer naming for object kinds those standards do not cover.

## Stage 5: Select a project profile and architecture

Read [project-profiles.md](references/project-profiles.md) in full. Select the smallest profile that covers the actual risk:

- `minimal`: low-risk, small, short-lived, or single-maintainer work.
- `standard`: maintained applications, services, integrations, or team-owned systems.
- `critical`: identity, authorization, payments, PII, regulated data, destructive migrations, or high availability/operational impact.

Never downgrade a project merely to reduce documentation. Explain any profile override.

Before declaring `ARCHITECTURE_READY` for a maintained, multi-module,
integration-heavy, or critical project, read
[codebase-design](../codebase-design/SKILL.md) in full. Confirm that proposed
modules hide coherent behavior, interfaces include caller-visible obligations,
seams are justified by real variation or isolation needs, and tests can
exercise behavior through observable interfaces. Do not force deep-module machinery onto a narrow minimal project.

## Stage 6: Materialize the project

If `--requirements-only` is absent:

1. Require a concrete target path and project name.
2. If an approved official initializer is selected, show its exact pinned
   command, prerequisites, target writes, network use, and dependency impact.
   Run its help/dry-run first and request approval before downloads. Never use
   `@latest`, an unpinned global CLI, or an upstream default branch as the
   production baseline.
3. Run the approved initializer into an empty target (or an isolated staging
   directory when ownership conflicts are expected). Then dry-run the Cerebro
   scaffold with `--merge` so every preserved conflict is visible. If no
   initializer is selected, dry-run Cerebro directly:

   ```bash
   python3 scripts/bootstrap_project.py \
     --target <path> \
     --name <name> \
     --profile <profile> \
     --agents <agents> \
     [--stacks sqlserver] \
     --stack-profile <working-stack-profile.json> \
     --dry-run
   ```

4. Show conflicts. Do not overwrite existing files unless the user explicitly authorizes merge or replacement. Run the scaffold without `--dry-run`.
5. Pass the approved selector output through `--stack-profile`; the scaffold
   writes it to `.cerebro/stack-profile.json` and pins its content hash in
   `.cerebro/project.json`. The stack profile must contain `status: approved`,
   the structured approval record, exact versions and normalized paths,
   source/pack refs, and selected rule IDs. Do not copy or hand-edit it after
   generation.
6. Replace generated `TBD` sections with the confirmed requirement package. Preserve `TBD` only for explicitly non-blocking unknowns and name an owner or resolution point.
7. Follow [document-contracts.md](references/document-contracts.md); do not duplicate policy across generated files.
8. Populate `docs/CONTEXT.md` with confirmed project-wide language. If multiple real bounded contexts were confirmed, also create `docs/CONTEXT_MAP.md` and `docs/contexts/*.md` lazily and route context-specific terms to their owner; do not infer contexts from folders or deployables alone.
9. Read [stack-layouts.md](references/stack-layouts.md), select the smallest source tree that matches the confirmed deployable units, and add stack-native source/test/config directories. Do not create speculative layers or empty services.
   When the approved stack includes SQL Server, pass `--stacks sqlserver`;
   this adds `docs/DATA.md` plus SQL-only team templates for procedures,
   scalar/inline table-valued functions, DML triggers, and table types under
   `database/templates/sqlserver/`. Populate an object template only after its
   DBHS input gate is complete. These are starter sources, not a requirement to
   create every object kind. Do not invent standards for uncovered objects.
10. Create ADRs only through `domain-modeling`'s decision gate. Keep the core record concise and add optional sections only when they preserve material reasoning.
11. Do not create `PROCESS.md`. Place durable rules in `AGENTS.md`, current state in `PROJECT_STATE.md`, and repeatable process in this plugin's skills.
12. Before any commit handoff, run the safety contract's Dissent and commit gates; scaffolding alone is not completion evidence.

## Stage 7: Configure agent adapters

- Always generate `AGENTS.md` as the shared, concise project instruction surface.
- Generate `CLAUDE.md`, `.claude/rules/`, and project-scoped Claude agents only when `claude` or `both` is selected.
- Do not copy the Cerebro skills into every generated project; the installed plugin remains their source.
- Keep agent files as indexes and routing rules, not duplicated project specifications.

## Stage 8: Offer optional tooling

Read [tooling-integrations.md](references/tooling-integrations.md) only when the user asks for tooling setup or the environment would materially benefit.

1. Detect whether each tool and integration is already present.
2. Report the exact detected version and configuration scope when verifiable.
3. Recommend project-scoped configuration before user-global configuration unless the user asks for a global default.
4. Explain the files or settings the tool will change.
5. Ask for explicit approval before installing or configuring it.
6. Verify after setup and record opt-in telemetry or privacy choices.
7. Require an official name or repository URL for any ambiguous tool. Never guess a package from a nickname.

Start detection with the bundled read-only command when it is available:

```bash
python3 scripts/check_tooling.py --target <path>
```

## Stage 9: Validate readiness

Run:

```bash
python3 scripts/validate_project.py --target <path>
```

The validator derives profile, agent adapters, features, stack-specific assets,
and the exact required-file plan from `.cerebro/project.json`. Legacy caller
flags are compatibility assertions only and fail when they conflict with the
manifest.

Do not report `IMPLEMENTATION_READY` unless:

- validation exits successfully
- no unresolved template tokens remain
- every blocking gate is resolved
- `.cerebro/project.json` matches the canonical scaffold plan and pins the
  installed stack profile
- `.cerebro/stack-profile.json` is approved, current, and internally consistent
- acceptance criteria have a verification method
- critical projects include security, rollback, observability, and recovery coverage
- the generated `PROJECT_STATE.md` names the first safe vertical slice and validation commands

## Final response

Report:

- selected profile and why
- final readiness state
- files created, updated, skipped, or conflicted
- confirmed assumptions and remaining non-blocking questions
- approved official references, exact stack versions, and Stack Pack versions
- validation commands and results
- optional tooling detected/configured/skipped
- first vertical slice and its definition of done
- canonical domain terms/contexts captured and ADRs created or deliberately skipped

Never claim production readiness merely because a directory tree was generated.
