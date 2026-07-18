# Adversarial Review Rules

## Why

The same model that planned or implemented a change may miss flaws caused by its own assumptions. Use a second model or independent review path to reduce echo-chamber bias.

## Rules

1. Reviewer must read direct artifacts, not only Claude's summary.
2. Reviewer must be skeptical and specific.
3. Reviewer must be read-only.
4. Reviewer must end with a clear verdict.
5. Claude must log accepted and rejected critiques.
6. Human final sign-off is required before code for plan reviews.
7. Deadlock is acceptable; false approval is not.

## Artifacts

- PLAN.md
- PLAN-REVIEW-LOG.md
- CODEX_REVIEW.md
- IMPLEMENTATION_REVIEW_LOG.md
