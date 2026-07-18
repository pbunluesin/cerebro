# Security Guide

## Secret Handling

- Do not commit `.env`, service account JSON, private keys, certificates, or production credentials.
- Use `.env.example` for names only.
- Never print secrets in logs, docs, screenshots, or issue comments.

## Authentication

`TBD`

## Authorization

`TBD`

## Input Validation

- `TBD`

## PII / Sensitive Data

| Data | Sensitivity | Storage | Access Rule |
|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` |

## Logging Rules

- Do not log passwords, tokens, API keys, or full payment details.
- Avoid logging unnecessary PII.
- Include correlation/request IDs where possible.

## Dependency Security

- [ ] Dependencies reviewed
- [ ] Known vulnerabilities checked
- [ ] Lockfile committed where applicable

## Security Review Checklist

- [ ] Auth path reviewed
- [ ] Authorization rules tested
- [ ] Secrets protected
- [ ] Input validation implemented
- [ ] Error messages do not leak sensitive details
- [ ] Logs reviewed
