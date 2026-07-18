# Example ADR: Use JSONL for BigQuery Export

This is an example only. Copy it into `project-root/docs/decisions/` only if relevant.

## Context

CSV ingestion can fail when source data contains quotes, commas, multiline text, inconsistent escaping, or mixed data types.

## Decision

Use JSONL as the preferred export format for BigQuery ingestion when source data contains complex text or mixed values.

## Consequences

Positive:

- More robust than CSV for complex text.
- Reduces quoting and multiline parsing issues.

Trade-off:

- Requires explicit serialization rules.
