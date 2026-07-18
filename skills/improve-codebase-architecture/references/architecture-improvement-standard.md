# Architecture Improvement Standard

## Contents

1. Evidence hierarchy
2. Hotspot selection
3. Candidate contract
4. Ranking and rejection
5. Selection gate

## Evidence hierarchy

Prefer, in order:

1. repeated user-visible defects or change failures tied to the structure
2. required changes that repeatedly span many callers/modules
3. tests demonstrating awkward or leaky interfaces
4. dependency/call traces showing duplicated policy or hidden coupling
5. version history showing recurring edits, corroborated by current code
6. maintainers' stated friction

File size, folder count, style preference, or churn alone is weak evidence.

## Hotspot selection

When the user does not name a target:

- inspect a bounded, representative Git history window
- group repeated changes by capability, not only by pathname
- exclude generated/vendor/migration-only noise
- check whether churn reflects active feature value rather than structural pain
- select a narrow area before deep inspection

State the history window and selection assumption. Do not scan the entire repository merely because tools make it cheap.

## Candidate contract

Each candidate must include:

- name and recommendation strength: `Strong`, `Worth exploring`, or `Speculative`
- exact files/modules and callers inspected
- concrete change, defect, or test friction
- current interface and leaked responsibility
- proposed responsibility shift, without pretending the final interface is decided
- dependency category and likely seam/adapter impact
- expected gains in locality, leverage, failure isolation, or testability
- affected tests and compatibility/migration burden
- accepted-decision or contract conflicts
- R0/R1/R2 classification and reversibility
- evidence that would falsify the recommendation
- cost of doing nothing

## Ranking and rejection

Rank requirement fit and observed pain above aesthetic consistency. Reject a candidate when:

- the proposed interface merely renames or layers the current behavior
- only one speculative future caller needs the abstraction
- the migration cost exceeds demonstrated change pressure
- an accepted decision still fits and no new evidence justifies reopening it
- a local fix provides the same outcome with lower blast radius
- tests cannot characterize the current contract enough for safe migration

No candidate is better than an unjustified refactor.

## Selection gate

Candidate discovery does not authorize design or implementation. After presentation:

1. obtain the user's candidate selection
2. grill constraints one at a time
3. compare alternative interfaces
4. write a bounded plan and acceptance evidence
5. obtain any approval required by risk and repository policy

Keep architecture assessment, interface design, and code mutation as separate reviewable stages.
