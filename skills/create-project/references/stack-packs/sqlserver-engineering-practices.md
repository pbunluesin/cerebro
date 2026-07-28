---
id: sqlserver-engineering-practices
guide_version: "1.0.0"
status: approved
authority: microsoft-derived-engineering-guidance
scope:
  - sqlserver-database-design
  - sqlserver-normalization
  - sqlserver-indexes
  - sqlserver-query-optimization
verified_at: "2026-07-28"
next_review_at: "2026-10-28"
---

# SQL Server Database Engineering Practices

This guide provides Microsoft-derived engineering defaults for SQL Server
database design, normalization, indexes, and optimization. Unlike `DBHS-01`
and `DBHS-02`, it is not a user naming/template policy. Exact workload,
version, compatibility level, edition, hosting, and operational evidence
decide context-sensitive choices.

## Contents

1. Applicability and evidence
2. Database design
3. Normalization and denormalization
4. Keys, relationships, and constraints
5. Data types and row design
6. Index design
7. Index maintenance
8. Query and database optimization
9. Function, trigger, and type performance
10. Verification gates
11. Rejected blanket rules
12. Update lifecycle

## 1. Applicability and evidence

Before applying an optimization:

- resolve SQL Server/Azure SQL target, engine version, compatibility level,
  edition/tier, hardware/resource limits, HA/replica topology, and deployment
  tooling;
- identify the business SLA and measured bottleneck;
- capture a baseline using Query Store, actual execution plans, runtime/wait
  statistics, representative data distribution, concurrency, and load shape;
- scope every rule to exact project-relative paths and database objects;
- distinguish data-integrity requirements from performance preferences;
- define rollback/forward recovery and post-change acceptance thresholds.

Do not apply a nearby-version feature, default maintenance threshold, index
recommendation, query hint, or denormalization because it is fashionable.

The team-mandated `READ UNCOMMITTED` GET procedure policy remains governed by
`DBHS-01`. This guide requires its result semantics and concurrency behavior to
be measured; it does not silently override the team policy.

## 2. Database design

- Model business entities, ownership, identifiers, lifecycle, and invariants
  before choosing tables.
- Give every persisted entity a stable candidate key and an explicit primary
  key decision.
- Use schemas for real ownership/security boundaries, not decorative grouping.
- Keep one authoritative representation for each fact.
- Express durable integrity in database constraints when SQL Server can enforce
  it; application checks alone are not concurrency guarantees.
- Define nullability intentionally. `NULL`, empty string, zero, “unknown,” and
  “not applicable” are different states unless requirements make them equal.
- Define defaults only for real domain defaults; never use a default to hide
  missing required input.
- Define temporal, audit, retention, deletion, history, reconciliation, and
  migration semantics from requirements rather than inferred column names.
- Choose surrogate and natural keys from stability, width, privacy,
  interoperability, and business identity. Preserve real candidate-key
  uniqueness even when a surrogate primary key is used.
- Avoid one generic EAV/key-value table for stable relational attributes unless
  the requirement and query/validation costs justify it.

## 3. Normalization and denormalization

Use third normal form as the default design checkpoint for transactional
relational data:

- 1NF: remove repeating groups and keep values atomic for the confirmed query
  and integrity model;
- 2NF: remove attributes dependent on only part of a composite key;
- 3NF: remove transitive dependencies so non-key facts depend on the key, the
  whole key, and not another non-key fact.

Normalization is a modeling tool, not a mandate to split every value:

- JSON, XML, spatial, hierarchy, or array-like representations require a real
  document/value-semantic requirement and validation/query strategy;
- bounded read models, aggregates, materialized summaries, columnstore
  structures, and caches may be intentionally denormalized;
- a denormalization decision must name the measured read benefit, duplicated
  facts, authoritative source, update/reconciliation mechanism, consistency
  window, failure recovery, and tests;
- never denormalize merely to avoid writing joins;
- never normalize across independent bounded contexts when that creates shared
  ownership and distributed change coupling.

## 4. Keys, relationships, and constraints

- Use `PRIMARY KEY` for entity integrity and `UNIQUE` constraints/indexes for
  additional candidate keys.
- Use foreign keys for confirmed referential integrity unless an explicit
  cross-system ownership boundary makes enforcement impossible.
- Define delete/update actions deliberately; never cascade destructive
  behavior by convenience.
- Index foreign-key columns when workload evidence shows join, lookup, parent
  update/delete, or concurrency benefit. SQL Server does not create that index
  merely because the foreign key exists.
- Use `CHECK` constraints for deterministic row-level domain rules SQL Server
  can enforce.
- Keep constraint predicates trusted and deployment-validated; do not leave
  integrity dependent on untrusted/disabled constraints.
- Do not duplicate the same invariant inconsistently across trigger,
  procedure, application, and ETL paths.

## 5. Data types and row design

- Use the narrowest type that represents the full valid domain and expected
  growth without truncation/overflow.
- Specify string/binary length and decimal precision/scale explicitly.
- Use Unicode types when the domain requires Unicode; do not double storage by
  habit or lose valid text through a non-Unicode type.
- Avoid `(n)varchar(max)`/`varbinary(max)` when a bounded value is known.
- Keep parameter and column types aligned to avoid truncation and implicit
  conversion that prevents useful index access.
- Store dates/times with explicit timezone semantics; select `date`,
  `datetime2`, or `datetimeoffset` from the contract rather than legacy habit.
- Do not store numbers/dates/booleans as free-form strings.
- Evaluate row width, off-row LOB storage, compression, memory grants, network
  payload, and index duplication before adding wide columns.

## 6. Index design

### 6.1 Start from workload evidence

- Design indexes for confirmed predicates, joins, ordering, grouping, and
  projection from representative workload evidence.
- Review existing indexes before adding one. Consolidate duplicate or
  near-duplicate definitions.
- Measure read benefit against write, logging, storage, memory, backup,
  replication, and maintenance costs.
- Keep write-heavy tables intentionally under-indexed rather than adding every
  missing-index suggestion.

### 6.2 Keys and included columns

- Put search/join/order columns needed for efficient access in the key in an
  order justified by equality/range/selectivity and caller patterns.
- Use `INCLUDE` for projection columns that do not need key ordering/search
  semantics.
- Keep keys and include lists narrow; a “cover everything” index can reduce
  page density, cache efficiency, and DML performance.
- Use unique constraints/indexes for true invariants. Uniqueness also gives the
  optimizer useful information.

### 6.3 Choose the index family deliberately

- Choose clustered key width, stability, uniqueness, and insertion pattern
  from workload evidence; do not assume every identity must or must not be
  clustered.
- Use filtered indexes for stable, selective subsets whose predicates match
  material queries.
- Use columnstore for measured analytic/scan/aggregation workloads, not as a
  blanket replacement for rowstore OLTP indexes.
- Use full-text, XML, spatial, or memory-optimized indexes only for their
  confirmed semantics and operational support.
- Treat partitioning as manageability/data-lifecycle architecture first; it is
  not an automatic query-speed feature.

### 6.4 Validate an index

Record:

- queries and plans before/after;
- seeks/scans/lookups and estimated-versus-actual rows;
- logical reads, CPU, duration, memory grant/spills, waits, and concurrency;
- DML/log/space/backup/replica effects;
- usage/operational statistics over a representative period;
- rollback/removal criteria.

Missing-index DMVs and tuning tools produce candidates, not approved DDL.

## 7. Index maintenance

- Do not rebuild/reorganize every index on a fixed schedule or fixed
  fragmentation threshold.
- Correlate page density and fragmentation with real workload degradation.
- In many workloads, page density matters more than fragmentation.
- Keep fill factor at `100`/`0` by default. Lower it only for measured page
  splits where the extra space/I/O trade-off is justified.
- Prefer updating statistics when stale/low-quality statistics—not physical
  index structure—caused the regression.
- Choose reorganize/rebuild, partition scope, online/offline, resumable,
  low-priority wait, `MAXDOP`, and scheduling from index size, edition/target,
  maintenance window, log/HA/replica capacity, and recovery needs.
- Review CPU, I/O, memory, transaction log, blocking, replica lag, tempdb, and
  storage headroom before maintenance.
- Measure performance before and after; remove maintenance that has no
  demonstrated benefit.

## 8. Query and database optimization

### 8.1 Observe before changing

- Enable and configure Query Store for SQL Server 2022+ databases unless a
  documented target/operations constraint prevents it.
- Retain enough query, plan, runtime, and wait history for the troubleshooting
  objective without allowing uncontrolled Query Store growth.
- Use actual plans and representative runtime evidence; estimated plans alone
  cannot prove cardinality, spills, or runtime waits.
- Optimize the material bottleneck, not the most visually complex query.

### 8.2 Query shape

- Keep predicates SARGable where an index access path is expected.
- Avoid functions/conversions on the indexed column side unless a computed
  column/index or other measured design supports it.
- Align parameter/column types and collations.
- Use set-based operations and batch boundaries appropriate to the workload;
  eliminate avoidable N+1 and cursor/per-row work.
- Return only required columns/rows and define deterministic pagination/order.
- Keep transactions as short as correctness permits and avoid external waits
  while holding locks.

### 8.3 Plans, parameters, and hints

- Verify statistics freshness and sampling quality before rebuilding indexes
  or forcing plans.
- Test representative parameter distributions and optional-filter behavior.
- Use SQL Server version-compatible parameter-sensitive plan features only
  after resolving compatibility level and workload fit.
- Treat query/table/join hints and Query Store hints as experienced last-resort
  controls. Record evidence, owner, exact scope, review/expiry trigger, and
  removal test.
- Never clear the entire plan cache or force a plan as an unexplained
  production troubleshooting shortcut.

### 8.4 Database configuration

Treat compatibility level, cardinality estimator, Query Store, automatic
statistics, RCSI/snapshot behavior, MAXDOP, cost threshold, memory settings,
tempdb, compression, automatic tuning, and Intelligent Query Processing
features as version/target/workload decisions. Do not copy an instance tuning
checklist into every database.

## 9. Function, trigger, and type performance

- Prefer inline relational forms when they expose useful costing and
  optimization.
- Verify scalar UDF inlining rather than assuming it; compare an inline
  expression/iTVF/join for material row paths.
- Keep trigger logic set-based, bounded, and minimal because it extends the
  firing statement's transaction and latency.
- TVPs are `READONLY` and have no column statistics. Test representative row
  counts and consider a staged/temp-table alternative only with evidence.
- Do not add indexes/constraints to a table type without a real uniqueness or
  access requirement.

## 10. Verification gates

Before approval:

```text
build the SQL project against the exact target
deploy to an isolated representative database
validate constraints with positive, boundary, and invalid data
capture Query Store/actual-plan/runtime baseline
run representative concurrency and application-driver tests
review index and query before/after evidence
review DML/log/storage/HA/replica impact
generate and review deployment report/script
exercise rollback or forward recovery
record exact command, target, exit status, and material output
```

Production performance cannot be declared from a synthetic single-user test
alone.

## 11. Rejected blanket rules

- “Every query needs an index.”
- “Every table needs an identity clustered primary key.”
- “Always put the most selective column first.”
- “Every foreign key must always have its own index.”
- “A covering index should include every returned column.”
- “Rebuild above 30%, reorganize above 5%.”
- “Set fill factor to 80 everywhere.”
- “Denormalization is always faster.”
- “Third normal form must never be violated.”
- “Query hints fix bad plans permanently.”
- “Partitioning automatically makes queries faster.”
- “Scalar UDF inlining guarantees scalar UDF performance.”

Each statement ignores workload, version, cost, or integrity evidence.

## 12. Update lifecycle

Version this guide independently:

- patch: link/wording clarification without changed rule meaning;
- minor: additive practice/source/rule;
- major: changed default, enforcement level, applicability, or removed rule.

For every update:

1. verify current Microsoft documentation for supported SQL Server targets;
2. update `guide_version`, dates, and source links;
3. update the `DBEP-01` version/hash registry;
4. update Good/Bad rows and version policy when applicability changes;
5. regenerate `rules.json`;
6. review semantic and project-profile diffs;
7. re-run validators and representative forward tests;
8. never auto-promote observed guidance or mutate existing projects.

## Authoritative sources

- [Index architecture and design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17)
- [Optimize index maintenance](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/reorganize-and-rebuild-indexes?view=sql-server-ver17)
- [Primary and foreign key constraints](https://learn.microsoft.com/en-us/sql/relational-databases/tables/primary-and-foreign-key-constraints?view=sql-server-ver17)
- [Database normalization basics](https://learn.microsoft.com/en-us/previous-versions/troubleshoot/microsoft-365/microsoft-365-apps/access/database-normalization-description)
- [Query Store](https://learn.microsoft.com/en-us/sql/relational-databases/performance/monitoring-performance-by-using-the-query-store?view=sql-server-ver17)
- [Query Store hints](https://learn.microsoft.com/en-us/sql/relational-databases/performance/query-store-hints-best-practices?view=sql-server-ver17)
- [Statistics](https://learn.microsoft.com/en-us/sql/relational-databases/statistics/statistics?view=sql-server-ver17)
- [Scalar UDF inlining](https://learn.microsoft.com/en-us/sql/relational-databases/user-defined-functions/scalar-udf-inlining?view=sql-server-ver17)
- [DML triggers with multiple rows](https://learn.microsoft.com/en-us/sql/relational-databases/triggers/create-dml-triggers-to-handle-multiple-rows-of-data?view=sql-server-ver17)
- [Table-valued parameters](https://learn.microsoft.com/en-us/sql/relational-databases/tables/use-table-valued-parameters-database-engine?view=sql-server-ver17)
