# Cerebro Architecture

## Design goals

1. One invocation can move a project from vague idea to implementation-ready structure.
2. Requirements are evidence-backed and traceable to acceptance criteria.
3. Project documentation is proportional to risk and complexity.
4. Codex and Claude share canonical workflows instead of maintaining copies.
5. Deterministic operations use scripts; judgment remains in skills.
6. Optional tools are detected and offered, never silently installed.
7. Every generated project starts with the same evidence, dissent, scope, reversibility, and workspace-boundary safety contract.
8. Claude Code implements and fixes; a freshly resolved current Codex model performs independent review.
9. Domain language and module-design vocabulary remain composable disciplines instead of being duplicated inside every workflow.

## Component ownership

| Component | Responsibility |
|---|---|
| `.codex-plugin/plugin.json` | Codex plugin identity and skill discovery |
| `.claude-plugin/plugin.json` | Claude Code plugin identity |
| `skills/create-project/` | End-to-end discovery, grilling, readiness, and scaffolding |
| `skills/audit-project/` | Existing-repository gap analysis and safe retrofit |
| `skills/domain-modeling/` | Canonical domain language, bounded contexts, and ADR gate |
| `skills/codebase-design/` | Deep-module vocabulary, seam strategy, and interface comparison |
| `skills/improve-codebase-architecture/` | Evidence-led architecture candidate discovery and grilling |
| `skills/review-plan/` | Independent pre-code plan challenge |
| `skills/review-code/` | Evidence-backed diff review |
| `skills/fix-findings/` | Reproduce-first correction workflow |
| `skills/handoff/` | Verified session and cross-repository handoff |
| `agents/` | Claude-only specialist adapters |
| `scripts/` | Plugin-maintainer validation |

## End-to-end state machine

```text
DISCOVERY
  -> inspect existing evidence
  -> identify the highest-value unknown
  -> ask one question with a recommendation
  -> update the decision ledger

REQUIREMENTS_READY
  -> validate goals, users, scope, behavior, data, risk, and acceptance
  -> resolve all implementation-blocking questions

ARCHITECTURE_READY
  -> define boundaries, complete module interfaces, justified seams,
     data ownership, security, operations, validation, and rollback
     proportional to the selected profile

IMPLEMENTATION_READY
  -> materialize project files
  -> validate structure and unresolved placeholders
  -> hand off the first vertical slice; do not silently implement it
```

The user may stop or revise at any checkpoint. A prototype request can bypass the full gate only when it is explicitly labeled disposable and its limitations are recorded.

## Generated project source of truth

| Information | Canonical location |
|---|---|
| Human quick start | `README.md` |
| Durable cross-agent rules | `AGENTS.md` |
| Claude-specific routing | `CLAUDE.md` when Claude is selected |
| Current phase, goal, risks, next action | `PROJECT_STATE.md` |
| Problem, goals, users, success measures | `docs/PRODUCT.md` |
| Requirements and acceptance criteria | `docs/REQUIREMENTS.md` |
| Canonical domain terms | `docs/CONTEXT.md` for project-wide language; `docs/contexts/*.md` for context-specific language |
| Bounded-context relationships | `docs/CONTEXT_MAP.md` when multiple contexts exist |
| System boundaries and flows | `docs/ARCHITECTURE.md` |
| Review invariants and verification | `docs/quality/REVIEW_CONTRACT.md` |
| Hard-to-reverse decisions | `docs/decisions/` |

Conditional documents cover APIs, data, security, testing, and operations. The project profile determines which are required.

## Compatibility

Both Codex and Claude discover skill folders under `skills/`. Claude-only custom agents live under `agents/` and do not duplicate canonical policy; they invoke the shared review/fix contracts. Generated projects use `AGENTS.md` as the shared instruction surface and add a concise `CLAUDE.md` adapter only when Claude support is selected.

Source-code directories are deliberately not hard-coded in the baseline scaffold. After the requirements establish the runtime, framework, deployable units, and ownership boundaries, `create-project` applies its stack-aware layout rules and the selected framework's official conventions. This avoids shipping empty microservices, speculative layers, or a monorepo without a real lifecycle boundary.

## Default delivery loop

```text
Claude Code plan/implement
  -> verified project checks
  -> resolve latest approved Codex model from current authoritative evidence
  -> Codex ephemeral read-only review of exact scope
  -> Claude reproduce/fix confirmed findings
  -> Codex re-review R0/R1 and high-risk fixes
```

The model ID is not pinned in repository templates because a pinned “latest” value becomes stale. Every review records the resolved model ID, evidence date, CLI version, and scope. If model resolution or Codex execution is unavailable, the workflow reports `BLOCKED` or `PARTIALLY VERIFIED`; Claude self-review is not mislabeled as independent review.
