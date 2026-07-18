# References

These are the official documentation sources used to validate this template as of June 2026.

- OpenAI Codex: Custom instructions with AGENTS.md
- OpenAI Codex: Customization and AGENTS guidance
- Anthropic Claude Code: How Claude remembers your project
- Cursor Docs: Rules
- GitHub Copilot Docs: Repository custom instructions
- GitHub Copilot Docs: Custom instructions support matrix

Key takeaways:

- Codex reads `AGENTS.md` before doing work and supports global/project-scoped guidance.
- OpenAI recommends keeping `AGENTS.md` small and focused on durable repo guidance.
- Claude Code uses `CLAUDE.md` for persistent project instructions and supports `.claude/rules/`.
- Claude treats `CLAUDE.md` as context, not hard enforcement.
- Cursor supports project rules and `AGENTS.md`.
- GitHub Copilot supports `.github/copilot-instructions.md` and path-specific `.github/instructions/*.instructions.md`.

## Claude Code Subagents

Claude Code project-level subagents live under `.claude/agents/`. User-level subagents live under `~/.claude/agents/`.

The review/fix layer uses project-level subagents by default so the behavior stays tied to this repository's `CODE_REVIEW.md`.
