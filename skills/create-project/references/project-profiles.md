# Project Profiles

## Contents

1. Selection rules
2. Minimal profile
3. Standard profile
4. Critical profile
5. Conditional documents
6. Profile escalation

## Selection rules

Select the smallest profile that covers the project's real blast radius. Size alone does not determine risk: a tiny authentication or migration utility may be `critical`.

Use `critical` when any of these apply:

- authentication, authorization, SSO, or tenant isolation
- payments, balances, billing, entitlements, or financial reconciliation
- PII, health, education, regulated, confidential, or legally retained data
- destructive data operations, backfills, schema migrations, or multi-system synchronization
- privileged automation or production infrastructure control
- contractual availability, high recovery cost, or safety impact

Use `standard` for maintained products, services, libraries, integrations, or team-owned applications without a critical trigger.

Use `minimal` only for low-risk, reversible, narrow work with simple operation and ownership.

## Minimal profile

```text
<project>/
├── README.md
├── AGENTS.md
├── CLAUDE.md                  # Claude or both only
├── PROJECT_STATE.md
├── .gitignore
├── docs/
│   ├── README.md
│   ├── PRODUCT.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── TESTING.md
│   └── decisions/
│       └── 0000-template.md
└── .claude/                   # Claude or both only
    └── rules/
        └── guardrails.md
```

Use concise documents. Omit empty API, data, and operations files when those concerns genuinely do not exist.

## Standard profile

```text
<project>/
├── README.md
├── AGENTS.md
├── CLAUDE.md                  # Claude or both only
├── PROJECT_STATE.md
├── .env.example
├── .gitignore
├── docs/
│   ├── README.md
│   ├── PRODUCT.md
│   ├── REQUIREMENTS.md
│   ├── CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── DATA.md                # when data persists or synchronizes
│   ├── API.md                 # when interfaces exist
│   ├── SECURITY.md
│   ├── TESTING.md
│   ├── OPERATIONS.md
│   ├── decisions/
│   │   └── 0000-template.md
│   └── quality/
│       ├── REVIEW_CONTRACT.md
│       └── findings/
│           └── .gitkeep
├── .claude/                   # Claude or both only
│   ├── rules/
│   │   ├── guardrails.md
│   │   └── docs-routing.md
│   └── agents/
│       ├── cerebro-reviewer.md
│       └── cerebro-fixer.md
└── .github/
    └── pull_request_template.md
```

## Critical profile

Include the standard profile plus:

```text
docs/
├── SECURITY.md                # include threat model and trust boundaries
├── DATA.md                    # include classification, retention, recovery
├── OPERATIONS.md              # include SLOs, alerts, rollback, DR, ownership
├── MIGRATION.md               # when migration/backfill/cutover exists
└── quality/
    ├── REVIEW_CONTRACT.md
    ├── THREAT_MODEL.md
    ├── RELEASE_CHECKLIST.md
    └── findings/
        └── .gitkeep
```

Critical projects require named evidence for security, rollback/recovery, observability, failure injection or recovery testing, and human approval of R0 operations.

## Conditional documents

Generate a document only when its concern exists:

| Condition | Document |
|---|---|
| Persistent or synchronized data | `docs/DATA.md` |
| API, event, webhook, file, queue, or vendor contract | `docs/API.md` |
| Migration, backfill, cutover, or compatibility window | `docs/MIGRATION.md` |
| Domain-specific terminology | `docs/CONTEXT.md` |
| Non-trivial security or privacy boundary | `docs/SECURITY.md` |
| Deployment or operated runtime | `docs/OPERATIONS.md` |

The scaffold creates the profile baseline. Remove an unused conditional document rather than keeping empty boilerplate, but never remove a document required by a critical trigger.

## Profile escalation

Escalate immediately when discovery uncovers a critical trigger. Record:

- the trigger
- newly required decisions and documents
- impact on timeline or validation
- whether previously accepted assumptions remain safe

Do not silently de-escalate. Require the user to remove the triggering scope or explicitly accept a documented exception that does not violate safety or policy.
