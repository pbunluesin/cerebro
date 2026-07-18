# Deep Module Design Standard

## Contents

1. Precise vocabulary
2. Depth and locality checks
3. Dependency and seam strategy
4. Design alternatives
5. Test and migration discipline

## Precise vocabulary

- **Module:** a cohesive capability with an interface and hidden implementation; scale may be a function, package, subsystem, or vertical slice.
- **Interface:** everything a caller must know, including operations, invariants, ordering, errors, configuration, consistency, and performance obligations.
- **Implementation:** behavior and internal structure hidden behind the interface.
- **Seam:** a location where behavior can vary without callers changing.
- **Adapter:** a concrete implementation that connects a dependency or transport at a seam.
- **Depth:** useful behavior hidden per unit of caller knowledge.
- **Leverage:** benefit delivered to many callers through one stable interface.
- **Locality:** the degree to which related behavior, changes, bugs, and verification remain concentrated.

Use other terms precisely rather than banning them:

- **API** is a wire or library contract and may be part of a module's interface.
- **Service** is valid for an independently operated capability, not as a synonym for every class.
- **System/trust boundary** describes ownership or security crossing.
- **Bounded context** describes where domain language and rules hold.

## Depth and locality checks

Ask:

1. If this module disappeared, would its complexity disappear or scatter into callers?
2. Does the interface expose nearly every implementation decision?
3. Can a behavior change be made and verified in one place?
4. Do callers repeat sequencing, validation, retry, mapping, or policy logic?
5. Can tests exercise observable behavior through the same interface callers use?

A pass-through can be justified by compatibility, policy enforcement, observability, security, or a real variation point. Require evidence rather than deleting it automatically.

## Dependency and seam strategy

Classify each dependency:

- in-process deterministic logic: usually keep internal; no adapter required
- local substitute available: test through the real local protocol when practical
- owned remote capability: define a port when transport or deployment genuinely varies
- external provider: isolate provider-specific behavior and test the owned contract with a controlled adapter/mock

Multiple real adapters strongly justify a seam, but adapter count is a heuristic, not a law. Compatibility, trust, volatility, or test isolation can justify a seam earlier; document the reason.

## Design alternatives

For consequential interfaces, compare at least two genuinely different shapes. Useful lenses:

- minimal interface with maximum hidden policy
- flexible interface for confirmed extension points
- common-path interface optimized for the dominant caller
- transport-independent port when a real remote seam exists

For each alternative show calls, invariants, error behavior, hidden implementation, dependencies, migration cost, and weak points. Compare requirement fit, depth, locality, seam placement, operational behavior, and reversibility. Recommend one; do not return an unranked menu.

## Test and migration discipline

- Test observable behavior at the module interface.
- Keep internal tests when they provide valuable fault localization or cover algorithms economically.
- Replace obsolete shallow-module tests only after new tests demonstrate behavior parity; never delete them on design principle alone.
- Characterize current behavior before changing a risky seam.
- Preserve compatibility or provide an explicit cutover and rollback path.
- Verify that new abstractions reduce caller burden instead of layering new names over the same complexity.
