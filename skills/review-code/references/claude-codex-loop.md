# Claude to Codex Review Loop

## Contents

1. Roles
2. Resolve the reviewer model
3. Prepare independent review
4. Run Codex read-only
5. Fix with Claude
6. Re-review and close

## Roles

- Claude Code owns planning, implementation, reproduction, and fixes.
- Codex owns the independent finding pass.
- The Claude coordinator may assemble scope and invoke Codex, but must not replace unavailable Codex review with its own review while calling it independent.
- Human approval remains required for R0 actions and any other explicit approval boundary.

## Resolve the reviewer model

Immediately before every review:

1. Consult the current official OpenAI model catalog or the organization's authoritative current-model policy.
2. Select the latest approved frontier model available to Codex for complex coding/reasoning review.
3. Compare it with any configured/default model; do not assume configuration is current.
4. Record the evidence date, exact model ID, Codex CLI version, and reasoning effort when configurable.
5. Pass the model ID explicitly with `--model`.

If current authoritative evidence or model access cannot be verified, stop with `BLOCKED: reviewer model unresolved`. Never silently fall back to an older model.

## Prepare independent review

Give Codex raw artifacts, not Claude's conclusion:

- exact diff/commit/base
- confirmed requirements and acceptance criteria
- relevant invariants and review contract
- baseline failures
- required verification commands
- explicit exclusions or frozen decisions

Do not prime Codex with “find the bug I think exists.” Preserve provider and context independence.

## Run Codex read-only

Prefer an ephemeral, read-only run and never use dangerous bypass flags:

```bash
# Uncommitted change
codex exec --ephemeral --ignore-user-config -s read-only \
  review --uncommitted --model <verified-model-id> \
  "Review against AGENTS.md and docs/quality/REVIEW_CONTRACT.md. Report only evidence-backed material findings."

# Commit
codex exec --ephemeral --ignore-user-config -s read-only \
  review --commit <sha> --model <verified-model-id> \
  "Review against AGENTS.md and docs/quality/REVIEW_CONTRACT.md. Report only evidence-backed material findings."

# Branch/base comparison
codex exec --ephemeral --ignore-user-config -s read-only \
  review --base <branch> --model <verified-model-id> \
  "Review against AGENTS.md and docs/quality/REVIEW_CONTRACT.md. Report only evidence-backed material findings."
```

Confirm the installed CLI syntax with `codex exec review --help`; CLI flags can change. The reviewer must not modify implementation files. Save durable output only inside `WORK_ROOT` when the project requests a finding artifact.

## Fix with Claude

For each confirmed finding:

1. Claude reads the raw Codex finding.
2. Reproduce the failure or establish equivalent invariant/contract evidence.
3. Reject stale, duplicate, speculative, or out-of-scope findings explicitly.
4. Apply the smallest fix.
5. Add regression evidence.
6. Run focused then required full verification.
7. Update the finding status only after evidence passes.

Do not bundle opportunistic refactoring with a finding fix.

## Re-review and close

Resolve the current reviewer model again and ask Codex to re-review when:

- the fix is R0 or R1
- security, auth, money, data, migration, concurrency, or external contracts are affected
- the fix materially differs from Codex's minimal correction direction
- the first review requested re-review

Close only when the regression evidence and required review pass. Record model ID, scope, verdict, commands, and residual risk. No findings means no material defect was established in scope; it does not prove defect absence.
