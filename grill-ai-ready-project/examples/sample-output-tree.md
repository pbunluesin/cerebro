# Sample Output Tree

```txt
project-root/
├── CLAUDE.md
├── README.md
├── CHANGELOG.md
├── .env.example
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   ├── PROJECT_STATE.md
│   ├── REQUIREMENTS.md
│   ├── CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── API_SPEC.md
│   ├── DEVELOPMENT.md
│   ├── TESTING.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   ├── TROUBLESHOOTING.md
│   ├── PROCESS.md
│   └── decisions/
│       └── ADR-0001-initial-project-standard.md
└── .claude/
    └── settings.example.json
```


## Optional Subagent Tree

```txt
.claude/
├── settings.example.json
└── agents/
    ├── codebase-cartographer.md
    ├── project-griller.md
    ├── docs-architect.md
    ├── api-contract-reviewer.md
    ├── data-model-reviewer.md
    ├── security-reviewer.md
    ├── deployment-reviewer.md
    └── implementation-readiness-reviewer.md
```


## Optional Codex Review Artifacts

```txt
PLAN.md
PLAN-REVIEW-LOG.md
docs/CODEX_REVIEW.md
docs/IMPLEMENTATION_REVIEW_LOG.md
.claude/agents/codex-review-coordinator.md
```
