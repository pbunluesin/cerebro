# Architecture Report Contract

## Contents

1. Delivery mode
2. Report structure
3. Candidate visual
4. Evidence and accessibility
5. Verification

## Delivery mode

Use this reference only when the user requests a visual or HTML artifact.

- Prefer an in-conversation Markdown table/diagram when it communicates the relationship clearly.
- For a durable HTML report, require an explicit destination inside `WORK_ROOT`.
- Use embedded CSS and inline SVG by default so the file remains self-contained and reviewable offline.
- Do not add CDN scripts, install renderers, open a GUI/browser, or write to an OS temp directory without the approval required by project/platform policy.
- If Mermaid is already available and requested, preserve its source beside a rendered or fallback representation; do not make understanding depend on network access.

## Report structure

1. Repository, baseline, scope, date, and exclusions.
2. Compact visual legend when diagrams use repeated shapes.
3. Ranked candidate cards.
4. One top recommendation with its falsification evidence.
5. Rejected speculative ideas and review limitations.

Each candidate card contains:

- recommendation strength and R0/R1/R2 class
- exact files/modules and evidence
- one-sentence observed friction
- current responsibility/interface
- proposed responsibility shift, explicitly not a final interface
- before/after visual when it adds information
- locality, leverage, failure-isolation, and test impact
- compatibility/migration burden and accepted-decision conflicts
- cost of doing nothing

## Candidate visual

Choose the smallest useful form:

- dependency/call flow for leaked responsibility
- sequence for repeated orchestration or round trips
- ownership map for scattered state or policy
- interface-versus-hidden-behavior comparison for shallow modules
- before/after module map for consolidation or seam movement

Keep before and after at the same level of abstraction. Label hypothetical elements as proposed. Never use diagram cleanliness as evidence that the proposal is correct.

## Evidence and accessibility

- Link every candidate to precise local files/lines in the accompanying prose.
- Do not encode meaning by color alone; add labels, patterns, or text.
- Provide text alternatives for diagrams.
- Keep contrast, font size, keyboard reading order, and responsive width usable.
- Avoid decorative dashboards, fake metrics, and recommendation scores without a defined basis.

## Verification

Before delivery:

- open/render the report only when authorized and an appropriate viewer is available
- verify it works without network access when advertised as self-contained
- check links, escaping, viewport layout, and diagram/text agreement
- report the exact artifact path, checks run, and any rendering not verified
