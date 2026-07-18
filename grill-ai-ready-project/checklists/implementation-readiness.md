# Implementation Readiness Checklist

Mark implementation readiness as `Ready`, `Partially Ready`, or `Not Ready`.

## Required

- [ ] Objective is clear
- [ ] Scope is clear
- [ ] Out-of-scope is clear
- [ ] Acceptance criteria exist
- [ ] Impacted modules/files are identified or discoverable
- [ ] Test/validation path exists
- [ ] Security/data impact is documented
- [ ] Rollback/deployment notes exist for production changes
- [ ] Open questions are non-blocking or explicitly accepted as risk

## Production Additions

- [ ] Secrets/config handling documented
- [ ] Monitoring/logging strategy documented
- [ ] Error handling and retry behavior documented
- [ ] Data migration/backfill plan documented if needed
- [ ] API contract documented if needed
- [ ] ADR created for hard-to-reverse decisions
