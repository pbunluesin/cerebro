---
id: sqlserver-function-trigger-type-house-standard
standard_version: "1.0.0"
status: approved
authority: user-team-policy
scope:
  - sqlserver-functions
  - sqlserver-triggers
  - sqlserver-types
adopted_at: "2026-07-28"
last_reviewed_at: "2026-07-28"
next_review_at: "2026-10-28"
---

# SQL Server Function, Trigger, and Type Team House Standard

This is mandatory user-team policy for SQL Server functions, triggers, and
user-defined types. It extends the comment, naming, No Magic, formatting,
versioning, and verification intent of `DBHS-01` without changing the stored
procedure standard.

## Contents

1. Authority and scope
2. Common input gate
3. Common naming
4. Common source header
5. Function standard
6. Trigger standard
7. Type standard
8. Deployment and version transitions
9. Verification
10. Exceptions and change control

## 1. Authority and scope

Apply this standard only when:

- the project selects SQL Server with an exact supported engine version,
  compatibility level, edition/target, and path scope;
- the confirmed architecture requires a function, trigger, or user-defined
  type;
- no narrower approved project exception replaces an exact rule.

This standard does not require these object types. Prefer the simplest
constraint, query, stored procedure, or application boundary that satisfies
the confirmed behavior. Do not create a function, trigger, or type only to
populate a template.

This version does not define naming for tables, views, indexes, constraints,
sequences, schemas, roles, synonyms, assemblies, or migrations.

## 2. Common input gate

Do not generate an object until the caller supplies or confirms:

- object kind and business purpose;
- owning schema and exact semantic name;
- caller/dependent objects and compatibility expectations;
- exact parameters, columns, SQL data types, lengths, precision/scale,
  nullability, collation, and result contract where applicable;
- engine version, compatibility level, SQL project/deployment mode, and
  supported target;
- permissions and execution context;
- author, creation date, and safe test example;
- replacement/deployment order and recovery path;
- expected workload, cardinality, and performance evidence where applicable.

Never invent a prefix, schema, author, column, event, dependency, audit field,
business rule, example data, or execution context.

## 3. Common naming

All names must:

- be lowercase;
- use `snake_case`;
- end with `_v<positive_integer>`;
- use a confirmed business/technical semantic stem rather than an unexplained
  abbreviation;
- be schema-qualified wherever SQL Server syntax permits.

Object-specific shapes:

```text
function: <purpose>_<module>_v<version>
trigger:  <timing>_<event>_<module>_v<version>
type:     <module>_<role>_v<version>
```

Examples:

```text
calculate_order_total_v1
list_active_user_v1
after_insert_order_v1
instead_of_delete_payment_v1
order_item_list_v1
```

These tokens describe semantics; they are not mandatory `fn_`, `tr_`, `udt_`,
or `tt_` prefixes. Do not add a prefix that the team did not approve.

Treat the suffix as a caller/dependency contract version:

- function: parameters, return type/shape, error/null behavior, determinism,
  permissions, and performance obligations;
- trigger: target, event/timing, side effects, recursion, ordering, failure,
  permissions, and transaction behavior;
- type: base/table shape, keys/checks, nullability, collation, permissions, and
  dependent procedure/function/client contracts.

## 4. Common source header

Every object source file begins with:

```sql
/*
------------------------|-------------------------------|---------------------------------------------
-- Author               | DateTime                      | Comment
------------------------|-------------------------------|---------------------------------------------
-- <Developer Name>     | <YYYY-MM-DD>                  | Create <OBJECT> V<version>: <Purpose>
------------------------|-------------------------------|---------------------------------------------

-- <OBJECT_TEST>:
-- <Safe, commented verification example>

-- PURPOSE:
-- <Business purpose and caller-visible behavior>
*/
```

Use these test labels:

- function: `SELECT_TEST`;
- trigger: `DML_TEST`, `DDL_TEST`, or `LOGON_TEST`;
- type: `DECLARE_TEST`.

The author must be confirmed. Do not use the AI model name as the author unless
the user explicitly requests it.

The source comment lives in the SQL project/script. SQL Server does not turn
that comment into persistent object metadata automatically. Add an extended
property only when the project separately confirms its name, ownership,
deployment support, and update behavior.

Every test example must remain commented, use safe synthetic values, state its
fixture/precondition, and run only against an isolated approved environment.

## 5. Function standard

### 5.1 Select the function kind explicitly

Choose and record one:

- inline table-valued function (iTVF);
- multi-statement table-valued function (MSTVF);
- scalar T-SQL function;
- CLR function only under a separately approved CLR/security/operations
  decision.

Prefer an inline relational expression/iTVF when it expresses the confirmed
set-based contract. Do not convert logic into a scalar or multi-statement
function for reuse alone.

### 5.2 Function contract

Every function must:

- declare explicit parameter and return types;
- define `NULL`, empty-set, divide-by-zero, overflow, collation, rounding, and
  error behavior where applicable;
- have no unconfirmed side effects or hidden cross-domain data access;
- schema-qualify referenced objects;
- use `SCHEMABINDING` only when its dependency and deployment restrictions are
  accepted and tested;
- keep SQL keywords uppercase, leading commas on continuation lines, and
  four-space indentation;
- end the GO-aware team source batch with `GO`.

### 5.3 Function performance

- Verify an actual execution plan from representative callers and data.
- For scalar UDFs, record whether the exact engine/compatibility level can
  inline the function and verify whether inlining actually occurred.
- Do not assume `is_inlineable = 1` means every calling query is inlined.
- Detect row-by-row invocation, lost parallelism, repeated data access,
  underestimated cost, spills, and cardinality problems.
- Compare an inline expression/iTVF/join alternative when the function is on a
  material row path.

## 6. Trigger standard

### 6.1 Trigger decision

Record why a trigger is required instead of an explicit constraint, stored
procedure, application service, scheduled job, CDC/event mechanism, or
deployment control. Hidden side effects are not accepted merely because a
trigger is technically possible.

Identify:

- DML, DDL, or logon trigger;
- exact target and scope;
- `AFTER`/`FOR` or `INSTEAD OF`;
- exact events;
- execution context and privilege boundary;
- recursion/nesting/order assumptions;
- failure and recovery behavior.

### 6.2 DML trigger behavior

Every DML trigger must:

- handle zero, one, and many affected rows;
- use `inserted` and `deleted` set-wise;
- avoid scalar assignment from `inserted`/`deleted`;
- avoid cursors and per-row loops;
- put `SET NOCOUNT ON;` at the start of the body;
- avoid starting an independent transaction; it executes inside the firing
  statement's transaction;
- bound work, locks, and side effects;
- avoid external/network calls;
- make an intentional error roll back/fail the firing contract;
- test INSERT, UPDATE, DELETE, multirow, zero-row, recursion, concurrency,
  permission, and forced-failure paths that apply.

### 6.3 Trigger version safety

Do not leave two active versions implementing the same target/event behavior.
A trigger version transition must:

1. identify every existing trigger on the target/event;
2. deploy/enable the new version and disable/drop the old version in one
   reviewed plan;
3. prove no duplicate side effect window exists;
4. include rollback/forward recovery;
5. re-run multirow, recursion, failure, permission, and concurrency tests.

DDL and logon triggers have broader blast radius. Treat changes as R1 at
minimum and R0 when lockout, availability, or irreversible external impact is
credible.

## 7. Type standard

### 7.1 Type decision

Identify whether the object is:

- user-defined table type used by TVPs/table variables;
- alias type;
- CLR user-defined type.

Do not use an alias or CLR type without explicit portability, security,
deployment, driver, and operations evidence. A table type is not a substitute
for a persisted normalized table.

### 7.2 Table type contract

Every table type must:

- declare explicit columns, types, lengths/precision/scale, nullability, and
  collation behavior;
- define only confirmed `PRIMARY KEY`, `UNIQUE`, or `CHECK` constraints;
- remain schema-qualified;
- document expected row-count range and ordering/uniqueness assumptions;
- account for TVP `READONLY` behavior and absence of column statistics;
- define required `EXECUTE`/`REFERENCES` permissions;
- verify the real client driver binding and representative row counts;
- keep SQL formatting consistent with the team standard;
- end the GO-aware source batch with `GO`.

### 7.3 Type version safety

SQL Server user-defined types are not altered in place; replacement normally
requires a new type and dependency migration.

For every type version:

1. inventory procedures, functions, client bindings, permissions, tests, and
   deployments that reference the old type;
2. create the new `_vN` type;
3. migrate dependents in an ordered compatibility window;
4. verify both versions while both are supported;
5. remove the old type only after no dependency remains and destructive
   approval is recorded.

Never drop/recreate a type merely to make deployment pass.

## 8. Deployment and version transitions

- Keep one declarative source file per object.
- Use the selected SQL project/deployment tool as the source of truth.
- Use `CREATE FUNCTION`, `CREATE TRIGGER`, and `CREATE TYPE` in SQL project
  object sources; use `CREATE OR ALTER` only where the approved standalone
  deployment mode and object syntax support it.
- Treat `GO` as a deployment-tool batch separator, not Database Engine syntax.
- Generate and review the deployment report/script.
- Review dependency ordering, permission changes, drops, locks, failure
  behavior, and rollback/forward recovery.
- Never deploy a trigger/type transition from an unreviewed generic template.

## 9. Verification

An object is incomplete until applicable evidence records:

- exact engine/compatibility/edition/target and SQL project build;
- name, schema, version, header, author, purpose, and safe test comment;
- parameter/column/return/event/type contract;
- caller/dependency compatibility;
- permissions using the real application role;
- representative data and execution plans;
- function inlining/parallelism behavior where material;
- trigger zero/one/many-row, recursion, failure, concurrency, and duplicate
  version behavior;
- type row-count/cardinality, `READONLY`, client binding, and migration order;
- isolated deployment plus report/script and recovery evidence;
- application integration tests through the real SQL Server driver.

“The DDL was generated” is not completion evidence.

## 10. Exceptions and change control

Every deviation records the exact rule/path/object/version, owner, reason,
caller/dependency impact, evidence, expiry/review trigger, and reversal path.

Version this standard independently:

- patch: clarification without changed enforcement/template output;
- minor: additive optional object variant or verification guidance;
- major: changed naming, mandatory header, object semantics, versioning, or
  deployment behavior.

For every change:

1. update `standard_version` and review dates;
2. update `DBHS-02` version/hash in `official-sources.json`;
3. update Good/Bad rules without reusing an ID for changed meaning;
4. update and validate templates;
5. regenerate `rules.json` and affected project profiles;
6. review semantic diffs and do not auto-apply them to existing projects.

## Authoritative behavior references

- [CREATE FUNCTION](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver17)
- [Scalar UDF inlining](https://learn.microsoft.com/en-us/sql/relational-databases/user-defined-functions/scalar-udf-inlining?view=sql-server-ver17)
- [CREATE TRIGGER](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-trigger-transact-sql?view=sql-server-ver17)
- [DML triggers with multiple rows](https://learn.microsoft.com/en-us/sql/relational-databases/triggers/create-dml-triggers-to-handle-multiple-rows-of-data?view=sql-server-ver17)
- [CREATE TYPE](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-type-transact-sql?view=sql-server-ver17)
- [Table-valued parameters](https://learn.microsoft.com/en-us/sql/relational-databases/tables/use-table-valued-parameters-database-engine?view=sql-server-ver17)
