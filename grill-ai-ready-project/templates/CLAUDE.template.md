# CLAUDE.md

## Project Summary

`TBD`: One-sentence project summary.

## Tech Stack

- Frontend: `TBD`
- Backend: `TBD`
- Database: `TBD`
- Cloud/Hosting: `TBD`
- CI/CD: `TBD`

## Read These First

Before implementation, read the relevant docs:

1. `docs/PROJECT_STATE.md`
2. `docs/REQUIREMENTS.md`
3. `docs/CONTEXT.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DATA_MODEL.md`
6. `docs/API_SPEC.md`
7. `docs/TESTING.md`
8. `docs/PROCESS.md`

## Key Commands

```bash
# install
TBD

# development
TBD

# build
TBD

# test
TBD

# lint/typecheck
TBD
```

## Working Rules

- Inspect existing code and docs before editing.
- Do not rewrite working modules unless the task requires it.
- Do not change database schema without checking `docs/DATA_MODEL.md`.
- Do not change API contracts without updating `docs/API_SPEC.md`.
- Do not change auth/security/payment/data-sync behavior without an implementation plan.
- Do not read, copy, or print secrets from `.env`, service account files, private keys, or credential files.
- Run validation commands before final summary when possible.

## Documentation Update Rules

After meaningful changes:

- Update `docs/PROJECT_STATE.md`.
- Update `CHANGELOG.md` for user-facing or operational behavior changes.
- Update `docs/REQUIREMENTS.md` if scope/acceptance criteria changed.
- Update `docs/API_SPEC.md` if endpoint contract changed.
- Update `docs/DATA_MODEL.md` if schema/data flow changed.
- Add an ADR under `docs/decisions/` for hard-to-reverse decisions with real trade-offs.

## Implementation Readiness

Do not begin implementation until the relevant requirement has:

- clear goal
- clear scope
- acceptance criteria
- validation path
- known impacted files/modules
- security/data impact reviewed
