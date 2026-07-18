# chaseai-yt/grill-me-codex Reference Summary

Source: https://github.com/chaseai-yt/grill-me-codex

This project adds a cross-provider review loop to Matt Pocock-style grilling:

- Claude grills and locks a plan into `PLAN.md`.
- Codex reviews the plan as a read-only adversarial reviewer.
- Codex returns `VERDICT: APPROVED` or `VERDICT: REVISE`.
- Claude revises, logs accepted/rejected critiques, and re-submits.
- The loop is bounded by `MAX_ROUNDS`.
- The user signs off before any code is written.

This skill package adapts the concept, but is MCP-first and keeps the broader AI-ready documentation standard.
