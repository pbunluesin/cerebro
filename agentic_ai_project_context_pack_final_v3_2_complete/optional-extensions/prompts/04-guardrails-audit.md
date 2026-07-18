# Prompt: Guardrails Audit

Audit the current task or pull request against the project guardrails.

Read:

- `AGENTS.md`
- `CLAUDE.md`
- `PROCESS.md`
- `docs/guardrails.md`
- `PROJECT_STATE.md`

Check:

1. NO MAGIC — Did the agent invent paths, services, APIs, DB objects, env vars, or business rules?
2. VERIFY BEFORE DONE — Is there evidence for every completion claim?
3. DISSENT — Were major changes challenged with blast radius, reversibility, and rollback?
4. SCOPE DRIFT — Did the task expand beyond requested scope?
5. R0/R1/R2 — Was reversibility classified correctly?
6. Learning Capture — Should any recurring mistake be recorded?
