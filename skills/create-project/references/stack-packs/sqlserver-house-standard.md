---
id: sqlserver-stored-procedure-house-standard
standard_version: "1.0.0"
status: approved
authority: user-team-policy
scope: sqlserver-stored-procedures
supported_actions:
  - get
  - insert
  - update
  - delete
adopted_at: "2026-07-28"
last_reviewed_at: "2026-07-28"
next_review_at: "2026-10-28"
---

# SQL Server Stored Procedure Team House Standard

This is the user's mandatory team standard. It is a project policy, not a
claim that every rule is a universal Microsoft or industry best practice.
When an approved project selects SQL Server and stored procedures, Cerebro,
Claude, and Codex apply this standard unless the project records an explicit
exception.

## Contents

1. Authority and applicability
2. Required input gate
3. Naming and contract versions
4. Header and `EXEC_TEST`
5. Parameters and schema evidence
6. Formatting
7. GET procedures
8. INSERT procedures
9. UPDATE procedures
10. DELETE procedures
11. Error and transaction structure
12. Known trade-offs and exceptions
13. Verification
14. Change control

## 1. Authority and applicability

Apply this standard only when all of these are true:

- the project selected the `sqlserver` Stack Pack with an exact supported
  engine version and project-relative path scope;
- stored procedures are part of the confirmed data-access contract;
- the generated or reviewed object is a `get`, `insert`, `update`, or `delete`
  procedure;
- the project has not approved a narrower exception for the exact rule and
  path.

This version does not define naming or templates for functions, triggers,
views, user-defined types, tables, indexes, or migrations. Do not infer those
standards from the stored procedure rules.

The project must resolve SQL Server/Azure SQL target, engine version,
compatibility level, edition, schema, and deployment tooling separately.

## 2. Required input gate

Do not generate production SQL until the caller supplies or confirms:

- action: `get`, `insert`, `update`, or `delete`;
- owning schema;
- module name and contract version;
- business purpose;
- target table or view and its owning schema;
- exact columns used by the procedure;
- parameter names, SQL data types, lengths/precision/scale, nullability, and
  defaults;
- result-set columns and ordering for GET;
- uniqueness and not-found behavior where applicable;
- transaction ownership and whether callers can already have an open
  transaction;
- author and creation date for the header;
- safe, non-secret example values for `EXEC_TEST`;
- required permissions and verification environment.

If a material item is missing, ask for it. Do not invent columns, audit fields,
business rules, schema names, example personal data, or external services.

## 3. Naming and contract versions

Procedure names must be lowercase and use:

```text
<action>_<module>_v<version>
```

Rules:

- `<action>` is one of `get`, `insert`, `update`, or `delete`;
- use `_` as the separator;
- `<module>` uses the confirmed team/domain term;
- `v<version>` is mandatory and uses a positive integer;
- schema-qualify both the definition and every referenced object;
- do not assume `dbo`; use the confirmed owning schema.

Examples:

```text
get_user_v1
insert_order_v1
update_student_v2
delete_payment_v1
```

The suffix is a caller-visible stored procedure contract version. Increment it
when a change breaks parameters, result sets, errors, permissions, transaction
behavior, or another confirmed caller obligation. Do not increment merely
because formatting or an internal implementation changed.

## 4. Header and `EXEC_TEST`

Every procedure must begin with the standard header:

```sql
/*
------------------------|-------------------------------|---------------------------------------------
-- Author               | DateTime                      | Comment
------------------------|-------------------------------|---------------------------------------------
-- <Developer Name>     | <YYYY-MM-DD>                  | Create SP V<version>: <Purpose>
------------------------|-------------------------------|---------------------------------------------

-- EXEC_TEST:
-- EXEC [<schema>].[<procedure>] <safe example parameters>

-- PURPOSE:
-- <Business purpose and caller-visible result or mutation>
*/
```

`EXEC_TEST` is mandatory, but it is an example rather than automated evidence.
It must:

- remain commented;
- use non-secret, non-production-specific values;
- name all parameters when omission or ordering could be ambiguous;
- identify required fixture/precondition in a nearby comment;
- never be run against production as part of generation.

For mutating procedures, validate the example in an isolated database. If the
verification harness uses a rollback transaction, it must also account for the
procedure's transaction ownership instead of assuming nested rollback is safe.

## 5. Parameters and schema evidence

- Use explicit SQL Server data types.
- Match length, precision, scale, nullability, collation-sensitive behavior,
  and identifier type to the confirmed schema and caller contract.
- Use meaningful parameter names.
- Allow `NULL` for optional GET filters only when `NULL` unambiguously means
  “filter not supplied.”
- Do not use a shorter or wider parameter type without checking conversion,
  truncation, and index-seek impact.
- Do not add `created_at`, `updated_at`, `reviewed_by`, or other audit fields
  unless the schema and requirement explicitly include them.
- List result columns explicitly. Do not use `SELECT *`.

## 6. Formatting

- SQL keywords use uppercase.
- Procedure and project-confirmed object names preserve the house naming
  convention.
- Put commas at the beginning of continuation lines.
- Use consistent four-space indentation.
- Align related column and value lists for readability.
- Terminate statements consistently with semicolons.
- Use `CREATE PROC` in the canonical team templates.
- End the procedure batch with `GO`; confirm that the selected SQL deployment
  tool recognizes this batch separator, or record a deployment-specific
  exception before removing it.
- Keep one declarative procedure definition per object file.
- Keep Markdown headings and fenced code blocks out of `.sql` files.

Example:

```sql
SELECT  t.column1
        , t.column2
        , t.column3
FROM    [schema_name].[table_name] AS t;
```

## 7. GET procedures

GET procedures follow the team policy:

- do not start an explicit transaction;
- put `SET NOCOUNT ON;` first in the body;
- set `TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`;
- support optional filters with the nullable filter pattern when required:

  ```sql
  WHERE (@param1 IS NULL OR t.column1 = @param1);
  ```

- return only confirmed columns;
- define deterministic ordering when caller-visible order matters;
- verify optional-filter plans using representative parameters and data.

`READ UNCOMMITTED` is an intentional house-policy choice. Section 12 records
its known semantics; do not silently remove it or falsely describe its results
as committed-consistent.

## 8. INSERT procedures

INSERT procedures must:

- put `SET NOCOUNT ON;` and `SET XACT_ABORT ON;` in the body;
- use the standard `TRY`/`CATCH` and transaction structure in section 11;
- use `IF NOT EXISTS` when the confirmed business contract requires duplicate
  prevention;
- use a database `PRIMARY KEY`, `UNIQUE` constraint, or unique index as the
  authoritative concurrency guarantee when duplicates are prohibited;
- handle the confirmed duplicate outcome without inventing a success/error
  contract;
- explicitly list inserted columns and values.

`IF NOT EXISTS` is a readability/business validation check. It is not by itself
a concurrency-safe replacement for a database uniqueness guarantee.

## 9. UPDATE procedures

UPDATE procedures must:

- put `SET NOCOUNT ON;` and `SET XACT_ABORT ON;` in the body;
- use the standard `TRY`/`CATCH` and transaction structure;
- validate target existence before the update;
- use the confirmed business error contract when no target exists;
- update only explicitly supplied and approved columns;
- keep the predicate narrow enough to protect the intended record set.

When concurrency can change existence between the validation and mutation,
the project must choose an isolation/locking/concurrency contract and test it.
The pre-check does not independently guarantee the later row state.

## 10. DELETE procedures

DELETE procedures must:

- put `SET NOCOUNT ON;` and `SET XACT_ABORT ON;` in the body;
- use the standard `TRY`/`CATCH` and transaction structure;
- validate existence when required by the confirmed behavior;
- distinguish “already absent,” “not permitted,” and “deleted” only when those
  are real caller-visible outcomes;
- apply the confirmed retention, soft-delete, foreign-key, and authorization
  contract before destructive behavior.

Deletion is not inferred from a procedure name. R0/R1 data-loss and rollback
controls still apply to deployment and execution.

## 11. Error and transaction structure

Every non-GET procedure follows this team structure:

```sql
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRAN;

    -- confirmed logic

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRAN;

    THROW;
END CATCH;
```

- Use `RAISERROR` for the team's business validation contract.
- Use `THROW;` inside `CATCH` to preserve the caught system error.
- Never swallow a failure or return success after rollback.
- Do not leave a transaction open or uncommittable.
- Confirm whether the procedure owns the transaction or supports being called
  inside an existing one.
- If caller-owned outer transactions are supported, adapt the template using a
  reviewed `@@TRANCOUNT`/savepoint strategy and verify both standalone and
  nested behavior. That adaptation requires a documented project exception
  because the base house template owns its transaction.

## 12. Known trade-offs and exceptions

These facts do not cancel the team policy; they prevent it from being presented
as a universal best practice:

- `READ UNCOMMITTED` allows dirty reads. Rows or values can appear, disappear,
  or change before the source transaction commits.
- `IF NOT EXISTS` followed by `INSERT` can race without an authoritative
  uniqueness constraint or a deliberately chosen locking/isolation strategy.
- existence checks before UPDATE/DELETE can become stale under concurrency.
- nested `BEGIN TRAN` does not create an independently committable inner
  transaction; a rollback can affect the caller's outer transaction.
- `RAISERROR` does not honor `SET XACT_ABORT` in the same way as `THROW`.
- nullable optional-filter predicates can produce parameter-sensitive plans.

An exception must record:

- exact rule ID and project-relative path;
- reason and caller-visible consequence;
- accountable owner;
- evidence and verification command/result;
- expiry or review trigger;
- migration/reversal plan.

Do not silently substitute another isolation level, error primitive,
transaction pattern, or naming convention.

## 13. Verification

A procedure is not complete until evidence covers the applicable items:

- SQL project build or parser validation against the exact target platform;
- procedure name, schema, action, and contract version;
- header, purpose, author, date, and commented `EXEC_TEST`;
- exact parameters and result/mutation contract;
- GET isolation behavior, including a dirty-read scenario;
- duplicate and concurrency behavior for INSERT;
- exists/not-found and concurrent-change behavior for UPDATE/DELETE;
- successful commit and forced-error rollback for non-GET;
- standalone and nested transaction behavior if nesting is supported;
- permissions through the real application database role;
- application integration through the real SQL Server driver;
- representative execution plans for optional filters and material queries;
- deployment report/script and recovery evidence.

Report the command, target, exit status, and material output. “The SQL was
generated” is not completion evidence.

## 14. Change control

This file is the canonical human source for the SQL Server stored procedure
team standard.

- Patch: clarification that does not change enforcement or generated SQL.
- Minor: additive action, rule, template, or optional capability.
- Major: changed naming, mandatory structure, error/isolation/transaction
  policy, removed rule, or incompatible template behavior.

For every change:

1. update `standard_version`, review dates, and affected sections;
2. update the `DBHS-01` registry entry and content hash in
   `official-sources.json`;
3. update Good/Bad rows without reusing an ID for changed meaning;
4. update SQL Server templates;
5. regenerate `rules.json`;
6. run repository, unit, template, and plugin validation;
7. regenerate and review affected project `.cerebro/stack-profile.json` files;
8. do not auto-apply semantic changes to existing projects.

## Authoritative behavior references

- [SET TRANSACTION ISOLATION LEVEL](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver17)
- [Transactions](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transactions-transact-sql?view=sql-server-ver17)
- [SAVE TRANSACTION](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/save-transaction-transact-sql?view=sql-server-ver17)
- [`@@TRANCOUNT`](https://learn.microsoft.com/en-us/sql/t-sql/functions/trancount-transact-sql?view=sql-server-ver17)
- [`THROW`](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/throw-transact-sql?view=sql-server-ver17)
- [Unique constraints](https://learn.microsoft.com/en-us/sql/relational-databases/tables/create-unique-constraints?view=sql-server-ver17)
- [`@@ROWCOUNT`](https://learn.microsoft.com/en-us/sql/t-sql/functions/rowcount-transact-sql?view=sql-server-ver17)
- [Optional parameter plan optimization](https://learn.microsoft.com/en-us/sql/relational-databases/performance/optional-parameter-optimization?view=sql-server-ver17)
