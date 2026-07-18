# Prompt: Claude Fix from Codex Review

Apply valid Codex review findings.

Process:

1. Read Codex findings.
2. Classify findings as valid / invalid / needs human decision.
3. Apply valid fixes only.
4. Preserve existing architecture and API contracts.
5. Run relevant checks.
6. Update `PROJECT_STATE.md`.
7. Update docs if behavior changed.
8. Summarize what was fixed and what was not fixed.
