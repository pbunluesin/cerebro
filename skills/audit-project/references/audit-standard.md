# Cerebro Audit Standard

## Contents

1. Evidence levels
2. Audit dimensions
3. Finding severity
4. Migration rules
5. Completion criteria

## Evidence levels

Classify each claim:

- `VERIFIED`: supported by code, configuration, executable checks, or authoritative external contract.
- `DOCUMENTED`: stated in project docs but not independently verified.
- `INFERRED`: supported indirectly; state the inference.
- `UNKNOWN`: insufficient evidence.
- `CONFLICTING`: credible sources disagree.

Do not upgrade `DOCUMENTED` to `VERIFIED` merely because multiple copied files repeat the same claim.

## Audit dimensions

### Product and requirements

- Outcome, users, success signals, scope, non-goals, and ownership are identifiable.
- Core behavior is expressed with stable requirement and acceptance IDs.
- Business invariants, failure behavior, and deferred scope are explicit.
- Requirements match observable code behavior or the difference is recorded.

### Agent guidance

- A concise root `AGENTS.md` routes agents to canonical context and verified commands.
- Nested guidance exists only where subtree rules differ.
- `CLAUDE.md` adds Claude-specific routing without copying shared requirements.
- Current tasks are absent from durable instruction files.
- The root safety contract explicitly covers No Magic, Verify Before Done, Dissent, Scope Drift Detection, R0/R1/R2, and an exact workspace deletion boundary.
- Outside-workspace deletion approval is per action and never implied by general write access.

### State and handoff

- `PROJECT_STATE.md` is short, current, and names the next safe action.
- It links rather than copies durable decisions, issue history, and architecture.
- Branch, commit, and check results are either current or clearly marked unverified.
- There is no competing state file unless scopes are explicit.

### Documentation architecture

- Each fact has one canonical owner.
- Documentation routes by concern rather than by agent/vendor.
- Conditional documents exist only when the concern exists.
- ADRs use one directory and capture real trade-offs.
- Local links and referenced files resolve.
- Generic template text is not mistaken for project knowledge.

### Architecture and contracts

- System boundary, module ownership, dependencies, data flow, trust boundaries, and failure handling are discoverable.
- Canonical domain terms are precise, implementation-free, and consistent across requirements, architecture, data, interfaces, tests, and code.
- Multiple bounded contexts have explicit ownership and relationships; folders or deployables are not mislabeled as contexts without evidence.
- Module interfaces hide coherent behavior; pass-through modules, leaked policy, and unjustified seams are identified as recommendations only when concrete change/test friction exists.
- APIs/events/webhooks/file contracts name versioning, auth, timeout, retry, idempotency, and compatibility where applicable.
- Sources of truth and data integrity rules are explicit.

### Security and privacy

- Assets, actors, sensitive data, authorization, tenant boundaries, secrets, logging restrictions, and threats are documented proportionally to risk.
- The repository does not contain obvious secrets or unsafe examples.
- Critical behavior has validation evidence, not only policy prose.

### Testing and delivery

- Install, run, lint/typecheck, test, build, and deployment commands are derived from the repository and verified where feasible.
- Acceptance criteria map to test or inspection evidence.
- Deployment, rollback/recovery, observability, ownership, and post-deploy verification match operational risk.

### Review and change governance

- Non-trivial changes have a project-specific review contract or equivalent.
- Review findings require a concrete failure path and precise evidence.
- Reviewer and fixer roles remain independent.
- R0/R1/R2 or an equivalent reversibility policy governs risky actions.
- Dissent runs before R0/R1 and every commit, with blast radius, assumptions, reversibility, and momentum blind spots.
- Scope drift is compared with the original goal rather than inferred only from diff size.
- When Claude implements and fixes, independent Codex review records provider, exact current model ID, resolution date, CLI version, scope, and verdict.
- R0/R1 and security/data/auth/money/migration/external-contract fixes receive fresh independent re-review.

### Optional tooling

- Tools are justified by the confirmed stack and workflow.
- Versions and integrations are detectable.
- Installation scope, telemetry, changed configuration, verification, and uninstall are documented.
- Missing optional tools do not make a project unready unless the project explicitly depends on them.
- RTK and Caveman are detected per agent; static validation and live integration tests are not conflated.

## Finding severity

- `CRITICAL`: current setup can cause secret exposure, unauthorized action, irreversible data loss, or unsafe production change.
- `HIGH`: agents are likely to implement materially wrong behavior because a core contract, source of truth, or validation path is missing or conflicting.
- `MEDIUM`: maintainability, context loading, or review reliability is degraded but a safe path remains discoverable.
- `LOW`: contained cleanup or clarity issue with limited operational consequence.

Distinguish findings from recommendations. A better style without a concrete failure mode is not a defect.

## Migration rules

Use this order:

1. Establish canonical destinations.
2. Copy or merge unique knowledge with provenance.
3. Update live references.
4. Add structural and content validation.
5. Confirm parity with source material.
6. Archive or delete legacy files only after Git diff and validation demonstrate no unique knowledge was lost.

Never combine durable process and volatile state merely to reduce file count. Move durable rules to `AGENTS.md` or skills; keep only current project status in `PROJECT_STATE.md`.

## Completion criteria

An audit is complete when:

- every material claim has an evidence level
- target profile and target tree are justified
- duplicate/conflicting sources are mapped
- blockers and safe assumptions are separated
- migration steps are ordered and reversible
- deletion candidates have explicit parity checks
- no file has been modified unless the user authorized retrofit work
