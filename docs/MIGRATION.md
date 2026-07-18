# Legacy Migration Map

This document records how the original source packs were consolidated into Cerebro `0.1.0`. The old files remain recoverable from Git history; they are not parallel runtime sources of truth.

## Migration rules

- Preserve behavior and attribution, not duplicate prose.
- Keep reusable judgment in skills, deterministic work in scripts, project facts in generated documents, and current status in `PROJECT_STATE.md`.
- Drop stack-specific defaults that are unsafe as universal policy.
- Delete a legacy source only after its replacement passes structural and behavioral validation.

## Source mapping

| Legacy source | Canonical replacement | Disposition |
|---|---|---|
| `grill-ai-ready-project/SKILL.md` and question bank | `skills/create-project/SKILL.md` and `references/requirements-gate.md` | Rewritten into one-question-at-a-time readiness workflow |
| Grill readiness/checklist files | Project profiles, requirement gate, document contracts, review/fix standards | Merged by concern and risk instead of copied checklists |
| Grill templates | `skills/create-project/assets/project/` | Rebuilt as minimal/standard/critical and conditional templates |
| Specialized Grill subagents | Shared review lenses plus the reviewer/fixer adapters | Consolidated to avoid default agent sprawl |
| Context pack `project-root/` | Generated project assets and document contracts | Rebuilt with one canonical owner per fact |
| Context pack `PROCESS.md` | `AGENTS.md`, Cerebro skills, and `PROJECT_STATE.md` | Split by durable rule, repeatable workflow, and current state; no replacement `PROCESS.md` |
| Context pack diagrams and explanatory HTML | `README.md`, `docs/ARCHITECTURE.md`, and profile trees | Replaced with maintained Markdown |
| Context pack Cursor/Copilot examples | None in the core plugin | Intentionally omitted; current scope is Codex and Claude |
| Language/vendor-specific rules | Stack-aware generation after requirements | Not safe as universal defaults |
| `codex-claude-reviewer/` | `skills/review-plan`, `skills/review-code`, `skills/fix-findings`, and `agents/` | Deduplicated and separated into reviewer/fixer responsibilities |
| `install-handoff-skill_V2.sh` | `skills/handoff/` | Replaced by plugin-distributed skill; no separate installer |
| `set-codex-model.sh` | None | Removed from plugin scope; it mutates user-global configuration and pinned model assumptions |
| Vendored upstream examples | `LICENSE-ATTRIBUTION.md` | Attribution retained; upstream snapshots removed from runtime tree |
| Current Matt Pocock domain/design/architecture concepts | `skills/domain-modeling`, `skills/codebase-design`, and `skills/improve-codebase-architecture` | Re-evaluated against current upstream and adapted to Cerebro paths, safety, evidence, and review contracts |

## Parity evidence

The consolidated plugin must pass all of the following before legacy deletion:

```bash
python3 scripts/validate_all.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/audit-project/scripts/audit_project.py --target .
claude plugin validate . --strict
```

The Codex plugin and each skill must also pass the official validators from the installed Codex skill/plugin creator packages.

## Intentional behavior changes

- Requirements are grilled one unresolved decision at a time instead of emitting an undifferentiated questionnaire.
- Readiness is traceable through `FR-###`, `NFR-###`, `BR-###`, `AC-###`, risks, assumptions, and blocking status.
- Generated documentation scales by actual risk through `minimal`, `standard`, and `critical` profiles.
- Claude and Codex use the same skills; Claude-specific files are thin adapters.
- Optional tools are detected and proposed, never installed or configured silently.
- Source layout is selected from confirmed deployable boundaries and stack conventions, not from a universal folder template.
- Domain terms are captured during grilling, multi-context maps are created only from real language/ownership boundaries, and architecture changes require evidence plus candidate selection before interface design.

## Verification result

Update this section only after the final clean-tree audit.

- Status: Passed; validators and behavior tests are green
- Legacy deletion: Complete; files remain recoverable from Git history
- Known unresolved integration: the exact identity of “Caseman”
