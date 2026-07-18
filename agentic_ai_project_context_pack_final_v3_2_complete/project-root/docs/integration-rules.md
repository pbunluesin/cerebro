# Integration Rules

## Purpose

Document business and technical rules for integrations with external systems.

## External Systems

| System | Purpose | Protocol | Owner |
|---|---|---|---|
| [Vendor/API] | [Purpose] | [REST/SFTP/DB/etc.] | [Owner] |

## Mapping Rules

| Source Field | Target Field | Rule |
|---|---|---|
| [source] | [target] | [mapping rule] |

## Business Rules

- [Rule]
- [Rule]
- [Rule]

## Retry / Failure Rules

| Scenario | Behavior |
|---|---|
| Timeout | [Retry/stop] |
| 4xx error | [Stop/log] |
| 5xx error | [Retry/escalate] |

## Vendor Contract Notes

- Vendor must confirm exact request body.
- Vendor must confirm auth header.
- Vendor must confirm expected response.
- Vendor must confirm idempotency behavior.
