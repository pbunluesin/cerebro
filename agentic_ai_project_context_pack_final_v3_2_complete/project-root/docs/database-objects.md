# Database Objects

## Purpose

Document tables, views, stored procedures, indexes, and important database semantics.

## Database Environment

- Engine: [SQL Server / PostgreSQL / BigQuery / Other]
- Version: [Version]
- Main database: [Name]
- Staging database: [Name]
- Linked servers / external sources: [List]

## Tables

| Table | Purpose | Key Columns | Notes |
|---|---|---|---|
| [table] | [purpose] | [keys] | [notes] |

## Views

| View | Purpose | Source Tables |
|---|---|---|
| [view] | [purpose] | [sources] |

## Stored Procedures

| Procedure | Purpose | Inputs | Outputs |
|---|---|---|---|
| [procedure] | [purpose] | [inputs] | [outputs] |

## Database Rules

- Document all joins that encode business meaning.
- Document all filters that affect active/inactive records.
- Document all null-handling behavior.
- Do not change stored procedure output shape without updating API/docs.

## Performance Notes

- [Index note]
- [Query plan note]
- [Batch size note]
