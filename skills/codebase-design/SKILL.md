---
name: codebase-design
description: Design or evaluate deep, cohesive software modules with small explicit interfaces, justified seams, testable dependency strategies, and high locality. Use when defining a new project's module structure; reshaping a module or package; deciding where an interface, port, adapter, API, or bounded-context boundary belongs; reducing pass-through layers; improving testability or AI navigability; or comparing alternative architecture designs before implementation.
---

# Codebase Design

Design modules that hide meaningful complexity behind an interface callers and tests can understand.

## Operating contract

- Read the closest project guidance, confirmed requirements, canonical domain language, architecture, tests, and accepted decisions.
- Start from required behavior and change pressure, not a preferred pattern or folder tree.
- Distinguish a module interface, runtime/API contract, seam, system boundary, trust boundary, and bounded context; do not collapse them into one generic word.
- Do not add an interface or adapter only to satisfy a style rule.
- Do not propose a broad refactor when a local correction satisfies the requirement.
- Remain design-only unless implementation is separately authorized.

Read [deep-module-design.md](references/deep-module-design.md) in full before approving a module or seam.

## Design workflow

1. Identify callers, required behavior, invariants, state ownership, failure modes, performance constraints, and expected change axes.
2. Draw the smallest useful system/module map and name each item with the project's domain language.
3. Define the candidate module's complete interface: operations plus caller-visible ordering, errors, configuration, consistency, and performance obligations.
4. Evaluate depth, leverage, and locality. Apply the deletion and pass-through tests; trace where complexity would move if the module vanished.
5. Classify dependencies and justify each seam and adapter. Keep test-only seams internal unless callers truly need them.
6. Produce at least two materially different designs when interface shape is consequential. Vary seam placement or caller experience, not just names.
7. Compare alternatives by requirement fit, interface burden, locality, failure isolation, test surface, migration cost, and reversibility.
8. Recommend one design, list the evidence that could overturn it, and identify any ADR-worthy choice.

If independent agents are explicitly authorized and available, they may generate isolated alternatives from the same raw constraints. Otherwise create alternatives sequentially and re-check each from first principles; do not pretend they are independent reviews.

## Completion

Report:

- selected module and interface
- what complexity it hides
- callers, dependencies, seams, and adapters
- alternatives considered and why rejected
- test strategy through observable interfaces
- migration/rollback path and risk class
- assumptions, unresolved contracts, and validation still needed

Do not equate a diagram or elegant type signature with validated architecture.
