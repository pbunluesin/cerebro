# Changelog

All notable changes to Cerebro are documented here.

## Unreleased

### Added

- Added a mandatory post-requirements Reference Selection Gate for current
  official scaffolds, documentation, and focused example repositories.
- Added versioned Good/Bad Stack Packs for Node.js, PHP, TypeScript, Next.js, React,
  NestJS, Vue, Tailwind, accessibility, PostgreSQL, and SQL Server.
- Added dependency-free deterministic pack extraction, exact-version/path rule
  selection, source freshness gates, and generated
  `.cerebro/stack-profile.json` records.
- Added canonical generated-project manifests, stack-profile hash pinning,
  symlink-safe scaffold writes, shared project scan/freshness policies, and
  adversarial readiness validation.
- Added the versioned `DBHS-01` SQL Server stored procedure team house standard,
  16 exact Good/Bad rule pairs, hash/freshness validation, and stack-conditional
  GET/INSERT/UPDATE/DELETE/transaction SQL templates.
- Added the versioned `DBHS-02` SQL Server function/trigger/type team standard,
  including Author/DateTime/Comment source headers, safe object tests,
  dependency-safe version transitions, and scalar-function, inline-table
  function, DML-trigger, and table-type starter templates.
- Added the versioned `DBEP-01` Microsoft-derived SQL Server engineering guide
  and exact Good/Bad pairs for database design, normalization, keys,
  constraints, data types, indexes, maintenance, Query Store, plans,
  statistics, query shape, parameters, hints, transactions, and configuration.

### Changed

- Made handoff explicit-only, restored deterministic Git-context collection, and expanded `PROJECT_STATE.md` with bounded operational continuation context.
- Added source-owned cross-project dispatches with authorized target inbox pointers and detailed SQL Server stored procedure contract verification.
- Moved the temporary technology guidance into canonical
  `skills/create-project/references/stack-packs/` sources and made
  observed-versus-approved upstream refs reviewable and easy to refresh.
- Classified the supplied SQL Server procedure convention as mandatory team
  policy rather than universal best practice, while preserving documented
  engine/concurrency trade-offs and scoped exception handling.
- Generalized local-reference hash/freshness/profile validation from a single
  SQL Server house standard to multiple house standards and engineering
  guides.
- Made approved selector provenance fail closed: structured approval identity,
  catalog-tied exact source refs, normalized project-relative paths, actual
  input hashes, canonical-bundle enforcement, and reproducible rule bindings.
- Added scheduled Stack Pack freshness enforcement, strict pinned Claude plugin
  validation, and non-masking shell syntax validation to CI.

## 0.1.0 - 2026-07-18

### Added

- Dual Codex and Claude Code plugin manifests.
- Requirement-grilling workflow with explicit readiness gates and traceability.
- Minimal, standard, and critical project profiles.
- Stack-aware project layout guidance and deterministic scaffold validation.
- Shared audit, plan-review, code-review, finding-fix, and handoff skills.
- Claude reviewer and fixer adapters.
- Read-only optional-tool detection with RTK integration status.
- Generated project guardrails, document contracts, and review controls.
- Default No Magic, Verify Before Done, Dissent, Scope Drift Detection, and workspace-boundary safety rules.
- Verified RTK and Caveman detection with baseline versus integration test guidance.
- Claude implementation/fix and latest-verified-Codex review/re-review workflow.
- Active domain-modeling, deep-module codebase-design, and evidence-led architecture-improvement skills.
- Multi-context domain mapping, inline terminology capture, compact ADR gating, and architecture candidate selection before interface design.

### Changed

- Replaced the legacy `PROCESS.md` model with `AGENTS.md`, reusable skills, and `PROJECT_STATE.md`.
- Consolidated duplicate source packs and prompts into canonical plugin components.
