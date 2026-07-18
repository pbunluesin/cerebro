# AI-Assisted Development Process

## Default Flow

1. Read `CLAUDE.md`.
2. Read `docs/PROJECT_STATE.md`.
3. Read relevant docs for the change.
4. Inspect existing code before editing.
5. Create a short implementation plan.
6. Implement the smallest safe vertical slice.
7. Run validation commands.
8. Update documentation.
9. Summarize changes, risks, and next steps.

## Before Editing Code

Confirm:

- [ ] Requirement is clear
- [ ] Acceptance criteria exist
- [ ] Impacted modules/files are known or explored
- [ ] Test/validation path exists
- [ ] Security/data impact reviewed

## Documentation Update Rules

- Update `docs/PROJECT_STATE.md` after every meaningful implementation step.
- Update `CHANGELOG.md` if behavior changed.
- Update `docs/API_SPEC.md` if API contract changed.
- Update `docs/DATA_MODEL.md` if schema/data flow changed.
- Add ADR only for hard-to-reverse decisions with real trade-offs.

## Commit / PR Rules

- Keep commits focused.
- Avoid unrelated refactors.
- Include validation result in PR summary.
- Explain skipped tests or unknowns.

## AI Agent Handoff

When context is getting large or another agent will continue:

1. Update `docs/PROJECT_STATE.md`.
2. Fill the `AI Agent Handoff` section.
3. List files to read first.
4. List files likely to change.
5. List validation commands.
6. List open questions and assumptions.


## Subagent Delegation Workflow

Use project-level subagents when available:

- `codebase-cartographer` maps an existing repo before questions are asked.
- `project-griller` pressure-tests unclear requirements.
- `docs-architect` maintains AI-ready documentation and ADR structure.
- `api-contract-reviewer` reviews APIs, webhooks, callbacks, and vendor contracts.
- `data-model-reviewer` reviews database, migration, sync, and source-of-truth decisions.
- `security-reviewer` reviews auth, secrets, PII, payment, and production risk.
- `deployment-reviewer` reviews deploy, rollback, observability, and operations.
- `implementation-readiness-reviewer` produces the final readiness gate.

The main Claude session must aggregate all findings into `docs/PROJECT_STATE.md` and related docs before implementation starts.


## Codex Review Process

Use Codex as an independent reviewer when work is high-risk or when the user requests second-model review.

### Before implementation

1. Lock the plan in `PLAN.md`.
2. Run Codex plan review through MCP-first, Codex CLI, or manual prompt.
3. Record rounds in `PLAN-REVIEW-LOG.md`.
4. Revise the plan or record rejected critiques with reasons.
5. Ask for final sign-off before coding.

### After implementation

1. Provide Codex with direct artifacts: `git diff`, changed files, test output, and relevant docs.
2. Record review findings in `docs/IMPLEMENTATION_REVIEW_LOG.md`.
3. Fix accepted issues.
4. Re-run validation.
