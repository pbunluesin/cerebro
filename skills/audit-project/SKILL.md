---
name: audit-project
description: Audit and safely retrofit an existing software repository against the Cerebro AI-readiness standard. Use when a user asks whether project context, Markdown structure, AGENTS.md, CLAUDE.md, requirements, guardrails, validation commands, review contracts, or handoff state are complete, duplicated, stale, or suitable for Codex and Claude; when migrating an older Cerebro/context-pack layout; or before applying the create-project standard to a non-empty repository. Report evidence and a migration plan before modifying files.
---

# Audit Project

Assess the repository that exists; do not grade it by template presence alone.

## Workflow

1. Read the closest `AGENTS.md` and project instructions.
2. Inspect Git status and preserve unrelated user changes.
3. Map the stack, entry points, tests, deployment, data, interfaces, security boundaries, and current documentation.
4. Run the read-only inventory:

   ```bash
   python3 scripts/audit_project.py --target <repo>
   ```

5. Read [audit-standard.md](references/audit-standard.md) in full.
6. Compare documented claims with code and configuration. Mark unverifiable claims as gaps; do not treat prose as evidence by itself.
7. Detect duplicate sources of truth, especially:
   - `PROCESS.md` versus `AGENTS.md`, skills, and `PROJECT_STATE.md`
   - root versus `docs/` copies of state or requirements
   - duplicate Claude/Codex requirement or architecture files
   - multiple ADR directories
   - copied reviewer/fixer prompts that diverge from canonical skills
8. Recommend `minimal`, `standard`, or `critical` based on actual risk.
9. Produce a migration map with `keep`, `merge`, `move`, `replace`, `archive`, and `delete-after-verification` actions.
10. Stop for confirmation before destructive migration, broad rewrites, global tool setup, or a profile decision that changes governance burden.

If the user's actual goal is to find deepening/refactor opportunities rather than documentation and AI-readiness gaps, route to [improve-codebase-architecture](../improve-codebase-architecture/SKILL.md). Do not turn a structural audit into an unsolicited architecture rewrite.

## Retrofit rules

- Preserve existing project knowledge even when its current file is poorly located.
- Prefer moving stable workflow rules into `AGENTS.md` or skills and current work into `PROJECT_STATE.md`.
- Remove `PROCESS.md` only after every live reference is updated and unique content has a canonical destination.
- Keep `CLAUDE.md` as a thin adapter to shared rules.
- Do not invent missing build/test commands. Derive and run them or record them as blocking.
- Do not install optional tools as part of an audit.
- Apply changes in reviewable stages and validate after each stage.

## Output

Report:

- current architecture and profile
- domain-language consistency and bounded-context ownership when applicable
- evidence-backed strengths
- findings grouped as critical/high/medium/low
- duplicate or conflicting sources of truth
- missing or unverifiable project knowledge
- target tree and migration map
- safe first migration stage
- validations required before deleting legacy files

If the user authorizes implementation, perform the smallest coherent stage, validate it, and show the diff before continuing to the next destructive stage.
