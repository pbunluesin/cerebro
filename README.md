# Cerebro

Cerebro is a dual Codex and Claude Code plugin for turning a rough software idea into an implementation-ready project.

It does not jump directly from an idea to code. It first inspects available context, grills one unresolved decision at a time, validates the final requirement set, selects a right-sized project profile, and then creates the project documentation, agent guidance, guardrails, and review workflow.

## Primary workflow

### Codex

```text
Use $create-project to grill this idea until implementation-ready, then scaffold the project: <idea>
```

### Claude Code

```text
/cerebro:create-project <idea>
```

The workflow progresses through:

```text
DISCOVERY -> REQUIREMENTS_READY -> ARCHITECTURE_READY -> IMPLEMENTATION_READY
```

Project files are generated only after blocking questions are resolved or explicitly recorded as accepted assumptions.

## Install

### Codex CLI

```bash
codex plugin marketplace add pbunluesin/cerebro --ref main
codex plugin add cerebro@cerebro
```

Start a new Codex session after installation, then invoke `$create-project`.

### Claude Code

```bash
claude plugin marketplace add pbunluesin/cerebro
claude plugin install cerebro@cerebro
```

For local development without installation:

```bash
claude --plugin-dir /absolute/path/to/cerebro
```

Restart Claude Code after a marketplace install or update, then invoke `/cerebro:create-project`.

## Included workflows

| Workflow | Purpose |
|---|---|
| `create-project` | Grill, validate, profile, and scaffold a new project |
| `audit-project` | Assess and retrofit an existing repository |
| `domain-modeling` | Sharpen ubiquitous language, context ownership, and durable decisions |
| `codebase-design` | Design deep modules, complete interfaces, and justified seams |
| `improve-codebase-architecture` | Find and grill evidence-backed architecture improvements |
| `review-plan` | Adversarial review before implementation |
| `review-code` | Evidence-backed review of a diff or explicit scope |
| `fix-findings` | Reproduce and fix one confirmed finding at a time |
| `handoff` | Preserve verified continuation context across sessions |

## Project profiles

- `minimal`: low-risk scripts, prototypes, and small internal tools
- `standard`: maintained applications, services, and team projects
- `critical`: auth, payments, PII, migrations, regulated data, or high operational risk

All profiles use `AGENTS.md` for durable shared rules and `PROJECT_STATE.md` for current status. Cerebro intentionally does not generate `PROCESS.md`; repeatable process belongs in skills.

During grilling, Cerebro actively resolves domain terminology and rejected synonyms. Maintained or multi-module projects also pass a proportional module/interface/seam check before `ARCHITECTURE_READY`; narrow projects are not forced into speculative abstraction.

## Default safety and delivery policy

Every generated project includes:

- No Magic: explicit assumptions and no invented infrastructure/services
- Verify Before Done: exact evidence before completion claims
- Dissent before R0/R1 changes and every commit
- Scope Drift Detection against the original goal
- R0 stop/ask, R1 disclose/proceed, and R2 proceed/verify behavior
- a strict project-root deletion boundary

Claude Code is the primary planner, implementer, and fixer. Codex performs independent read-only review with the latest currently verified approved model, and re-reviews high-risk fixes.

## Development validation

```bash
python3 scripts/validate_all.py
python3 -m unittest discover -s tests -p 'test_*.py'
claude plugin validate . --strict
```

See [the architecture](docs/ARCHITECTURE.md) for component ownership and [the migration map](docs/MIGRATION.md) for the legacy consolidation decisions.
