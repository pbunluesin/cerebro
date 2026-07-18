# Cerebro contributor guidance

## Purpose

Cerebro is a dual Codex and Claude plugin. It grills a software idea until the requirement set passes an implementation-readiness gate, then creates a right-sized project structure with durable agent guidance, documentation, guardrails, and review workflows.

## Read first

1. Read `PROJECT_STATE.md`.
2. Read `docs/ARCHITECTURE.md` for component ownership.
3. Read the `SKILL.md` for the workflow being changed.
4. Read only the references and assets named by that skill.

## Source-of-truth rules

- Keep reusable workflows in `skills/*/SKILL.md`.
- Keep detailed workflow policy in each skill's `references/` directory.
- Keep generated project files in `skills/create-project/assets/project/`.
- Keep deterministic file generation and validation in skill-local `scripts/`.
- Keep Claude-only subagents in `agents/`; Codex and Claude share `skills/`.
- Do not create `PROCESS.md`. Put durable rules in `AGENTS.md`, repeatable processes in skills, and current status in `PROJECT_STATE.md`.
- Do not copy the same policy into multiple files. Link to the canonical source.
- Keep legacy source mapping in `docs/MIGRATION.md`; do not restore parallel runtime copies from Git history.

## Safety contract

- NO MAGIC: inspect first, make every assumption explicit, and never invent hidden infrastructure, services, contracts, or business rules.
- VERIFY BEFORE DONE: editing is not completion. Run relevant checks and report exact evidence; never say “should work” as a completion claim.
- DISSENT: before every R0/R1 change and every commit, surface blast radius, assumptions, reversibility, and momentum blind spots.
- SCOPE DRIFT DETECTION: compare the stated goal with actual execution and flag accumulated extras, promoted nice-to-haves, and focused fixes turning into broad refactors.
- WORKSPACE BOUNDARY: never delete, move, overwrite, or recursively mutate anything outside `/Users/phatthab/Github/cerebro` without explicit approval for that exact action. Outside-root approval never persists.
- ONE QUESTION AT A TIME: during requirements grilling, ask only the highest-value unresolved question.
- NO PREMATURE BUILD: do not generate implementation code before the readiness gate passes unless the user explicitly requests a disposable prototype.
- SECRET SAFETY: never copy credentials, private keys, tokens, or production data into project artifacts.

## Change risk

- `R0`: irreversible or externally consequential. Stop, show exact target/impact/recovery limits, and obtain explicit approval immediately before execution.
- `R1`: costly to reverse. Within an authorized goal, disclose why, blast radius, validation, and rollback; then proceed unless another rule requires approval.
- `R2`: easily reversed and within scope. Proceed without permission, keep it narrow, and verify normally.

When uncertain, use the higher risk class. Risk class does not replace any stricter platform approval or security rule.

## Default delivery loop

1. Claude Code is the primary planner, implementer, and finding fixer.
2. After a non-trivial change, invoke Codex as an independent read-only reviewer against an explicit diff/commit.
3. Resolve the latest approved Codex review model immediately before each review from current authoritative evidence; record the exact model ID. Never silently fall back to an older/configured model.
4. Claude Code reproduces and fixes confirmed Codex findings one at a time.
5. Codex re-reviews every R0/R1 fix and any change affecting security, data, auth, money, migrations, or external contracts.

Keep review and fixing in separate contexts. A Claude agent may coordinate the Codex CLI but must not substitute its own self-review when independent Codex review is required.

## Validation

Run after changing plugin structure or skills:

```bash
python3 scripts/validate_all.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/create-project/scripts/check_tooling.py --target .
bash -n scripts/*.sh skills/*/scripts/*.sh 2>/dev/null || true
```

Inspect `git diff` and `git status -sb` before reporting completion.
