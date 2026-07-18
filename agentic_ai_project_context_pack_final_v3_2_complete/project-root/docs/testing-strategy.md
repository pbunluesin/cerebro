# Testing Strategy

## Purpose

Document how the project is tested and validated.

## Test Types

| Type | Purpose | Command / Method |
|---|---|---|
| Unit test | Validate isolated logic | `[command]` |
| Integration test | Validate system boundaries | `[command]` |
| API contract test | Validate request/response compatibility | `[command]` |
| Database test | Validate SQL/stored procedure behavior | `[command]` |
| Dry-run | Validate external sync without side effects | `[command]` |
| Regression test | Prevent known issue recurrence | `[command]` |

## Required Checks Before Commit

- [ ] Lint
- [ ] Type check
- [ ] Unit tests
- [ ] Integration tests or dry-run
- [ ] Manual verification notes if automation is not available

## Test Data

- Location: [Path / DB / fixture]
- Sensitive data handling: [Masking/anonymization rule]

## Known Testing Gaps

| Gap | Risk | Mitigation |
|---|---|---|
| [Gap] | [Risk] | [Mitigation] |
