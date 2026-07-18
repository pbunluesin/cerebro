# Stack-Aware Source Layouts

## Contents

1. Selection principles
2. Baseline layouts
3. Framework initialization
4. Tree validation

## Selection principles

The documentation profile and source layout solve different problems. Select the documentation profile from risk; select the source layout from deployable units, runtime boundaries, and ownership.

- Prefer one deployable unit until requirements prove that more are needed.
- Follow the selected framework's current official conventions when they exist.
- Keep source beside its tests unless the ecosystem strongly favors a separate test tree.
- Separate domain logic from external adapters only when both are real.
- Do not create `utils`, `common`, `shared`, `core`, or `services` as catch-all directories.
- Do not create a monorepo solely because the project has a frontend and backend; require independent lifecycle, ownership, or reuse.
- Give every generated directory a current purpose. Omit future placeholders.

## Baseline layouts

Use these as decision patterns, not mandatory names.

### Small application or automation

```text
src/
tests/
scripts/                  # only repeatable operator/developer tasks
```

### Maintained service

```text
src/
├── <domain-or-feature>/
├── adapters/             # only actual database/vendor/transport adapters
└── entrypoint.<ext>
tests/
├── unit/
├── integration/
└── contract/             # only when external contracts exist
```

Prefer vertical domain or feature slices over folders named only by technical layer when changes normally span those layers.

### Web application with one lifecycle

```text
src/
├── app-or-routes/
├── features/
└── server-or-api/        # only when deployed with the same lifecycle
tests/
public/                   # only for real static assets
```

Use the framework's official names when they differ.

### Multiple independently deployed applications

```text
apps/
├── <app-a>/
└── <app-b>/
packages/                 # only packages consumed by more than one app
tests/                    # only cross-application or system tests
```

Record package boundaries, dependency direction, release ownership, and integration tests. Avoid a shared package that becomes an unowned dumping ground.

### Reusable library or SDK

```text
src/<package>/
tests/
examples/                 # executable, tested usage only
```

The public API, compatibility policy, supported runtimes, packaging command, and release checks must be explicit.

### Data or event pipeline

```text
src/
├── ingestion/
├── transforms/
├── delivery/
└── contracts/
tests/
├── fixtures/             # synthetic and safe
├── contract/
└── reconciliation/
```

Create only stages that exist. Document replay, deduplication, schema evolution, backfill, recovery, and ownership before implementation.

### Infrastructure repository

```text
modules/                  # reusable units only
environments/
tests-or-policy/
scripts/
```

Require a preview/plan workflow, secret boundary, state ownership, drift policy, rollback or forward-recovery strategy, and protected production approval.

## Framework initialization

When the stack has an official initializer:

1. Verify the official package and supported runtime version.
2. Pin or record the initializer version when reproducibility matters.
3. Dry-run or show help when supported.
4. Explain which files it creates and whether it downloads dependencies.
5. Obtain approval before network access, package installation, or a non-empty target rewrite.
6. Run it into a safe empty/staging location when conflict behavior is uncertain.
7. Merge only confirmed stack files with the Cerebro documentation scaffold.
8. Record exact install, run, test, lint/typecheck, and build commands in `AGENTS.md` and `PROJECT_STATE.md` after verifying them.

Do not retain generated example code, telemetry defaults, or services that contradict the final requirements.

## Tree validation

Before declaring implementation readiness, confirm:

- every deployable unit has an owner, entry point, validation command, and release path
- dependency direction is visible and does not form an accidental cycle
- tests align with real boundaries and acceptance criteria
- generated directories are not empty promises
- configuration and secrets are separated
- migrations, generated artifacts, caches, and build output have explicit locations
- the repository tree matches `docs/ARCHITECTURE.md`
