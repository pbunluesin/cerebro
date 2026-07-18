---
name: improve-codebase-architecture
description: Find, rank, and grill evidence-backed architecture improvements in an existing codebase without starting a speculative rewrite. Use when a repository has repeated change friction, shallow/pass-through modules, scattered business logic, leaky seams, hard-to-test orchestration, unclear ownership, or recurring architecture pain; when a user asks for an architecture health scan or refactor candidates; or after audit-project identifies structural design debt. Present candidates first and do not modify code until the user selects a direction.
---

# Improve Codebase Architecture

Turn observed change and testing friction into a small set of defensible architecture candidates.

## Operating contract

- Read the closest `AGENTS.md`, `PROJECT_STATE.md`, canonical domain context, architecture, tests, and accepted decisions.
- Inspect Git status and preserve unrelated work.
- Scope before scanning. Prefer a user-named subsystem; otherwise use recent history and repeated change paths as attention signals, not proof of bad design.
- Separate current defects, architecture friction, and optional design improvements.
- Do not create code, interfaces, reports, or ADRs merely to make the review look complete.
- Stop before implementation. Candidate selection and implementation authorization are separate decisions.

Read [architecture-improvement-standard.md](references/architecture-improvement-standard.md) in full. Use [domain-modeling](../domain-modeling/SKILL.md) for domain-language changes and [codebase-design](../codebase-design/SKILL.md) only after a candidate is selected for interface exploration.

## Workflow

### 1. Establish evidence and scope

1. Record the stated pain, target paths, baseline commit, and exclusions.
2. If no target is named, inspect a representative Git history window for repeated change clusters, then corroborate with code, tests, and issues available in scope.
3. Trace real entry points, callers, dependencies, state, failure paths, and test surfaces for the selected area.
4. Record contradictions with domain context or accepted decisions; do not silently re-litigate them.

### 2. Build candidates

Look for evidence of:

- business behavior scattered across callers
- pass-through modules whose interface burden nearly matches their implementation
- changes that require synchronized edits in many places
- dependencies created internally that make realistic tests difficult
- interfaces that leak storage, transport, ordering, or failure details unnecessarily
- seams that exist without real variation, or missing seams where behavior genuinely varies

Apply the no-change alternative and deletion test to every candidate. Reject candidates supported only by taste, file size, layer count, or generic best practice.

### 3. Present before designing

Present a concise Markdown comparison by default. Use a diagram only when it materially clarifies calls, ownership, dependencies, or before/after state. Create an HTML report only when the user asks for one; do not introduce CDN or browser dependencies as a default workflow.

When the user requests a visual or HTML artifact, read [architecture-report.md](references/architecture-report.md) in full and follow its self-contained, evidence-first format.

For each candidate include evidence, affected files, concrete friction, proposed responsibility shift, expected locality/leverage, test impact, decision conflicts, confidence, risk class, migration outline, and the cost of doing nothing. Recommend one candidate but do not propose its final interface yet.

Ask which candidate the user wants to explore.

### 4. Grill the selected candidate

Once selected:

1. ask one highest-impact question at a time about constraints, dependencies, seam placement, compatibility, migration, and surviving tests
2. update confirmed domain terminology through `domain-modeling`
3. use `codebase-design` to compare materially different interfaces
4. identify ADR-worthy decisions without creating them automatically
5. produce a bounded refactor proposal with acceptance evidence, rollback, and an explicit no-go boundary

Route implementation to the normal plan-review, Claude implementation, Codex review, Claude fix, and high-risk re-review workflow.

## Completion

Report scope, evidence inspected, ranked candidates, selected/no-selection status, rejected speculative ideas, checks run, limitations, and the exact next authorized action. No candidate is a valid outcome when evidence does not justify a refactor.
